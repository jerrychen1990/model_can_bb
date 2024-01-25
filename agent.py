#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/01/25 10:35:09
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import os
from typing import List
from pydantic import BaseModel
from snippets.logs import get_file_log


LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

logger = get_file_log(name=__name__, log_dir=LOG_DIR)


def get_client(model_config:dict):
    model_type = model_config["model_type"]
    if model_type.upper() == "ZHIPU":
        import zhipuai
        api_key = model_config.get("api_key", os.environ.get("ZHIPU_API_KEY"))
        client = zhipuai.ZhipuAI(api_key=api_key) # 填写您自己的APIKey
    return client


class Claim(BaseModel):
    side: str
    content: str

class Message(BaseModel):
    claim: Claim
    name: str
    content: str



class Debater:
    def __init__(self, name:str, model_config:dict) -> None:
        self.name=name
        self.client = get_client(model_config)
        self.chat_kwargs = model_config.get("chat_kwargs", {})      
        self.model = model_config["model"]  
        
        
    
    def debate(self, claim:Claim, system:str, history:List[Message])->str:
        prompt = f'''给出你的发言，需要满足以下几个目标:
- 要能支撑你的论点:{claim.content}
- 可以使用推理、举例、煽动情绪等手段
- 需要对对方的论述做出回应
- 不要超过200字
论述：'''
        
        
        messages = [dict(role="assistant" if m.claim==claim else "user", content=m.content) for m in history]
        if not messages:
            messages.append(dict(role="user", content=prompt))
        else:
            last_user = messages[-1]
            last_user["content"] = last_user["content"]+"\n"+prompt
        
        messages.insert(0, dict(role="system", content=system))
        logger.info(f"messages: {messages}")
        resp = self.client.chat.completions.create(model=self.model, messages=messages, stream=False, **self.chat_kwargs)
        message = resp.choices[0].message.content
        return message
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return str(self)
    
class Judger:
    def __init__(self, name:str, model_config:dict) -> None:
        self.name=name
        self.client = get_client(model_config)
        self.chat_kwargs = model_config.get("chat_kwargs", {})      
        self.model = model_config["model"]  

    def judge(self, topic:str, pos_claim:Claim, neg_claim:Claim, history:List[Message])->str:
        system = '''你是一个公正的辩论评委，你现在要给一场辩论给出你的判断。
辩论主题:{topic}
正方观点:{pos_claim}
反方观点:{neg_claim}
以下是辩论记录:
{records}
   
'''
        prompt = '''请输出你更认同的观点（正方/反方），一定要选出一个，以及相关理由(200字以内)，理由不要自己想，需要和前面辩手们的发言内容相关。输出需要符合如下格式:
理由：
认同观点： 
'''
        records = [f"{m.name}发言:{m.content}" for m in history]
        records = "\n".join(records)
        system = system.format(topic=topic, pos_claim=pos_claim.content, neg_claim=neg_claim.content, records=records)
        messages = [dict(role="system", content=system), dict(role="user", content=prompt)]
        logger.info(f"messages:{messages[0]['content']}")
        resp = self.client.chat.completions.create(model=self.model, messages=messages, stream=False, **self.chat_kwargs)
        message = resp.choices[0].message.content
        return message
        
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return str(self)
    


if __name__ == "__main__":
    model_config = dict(model_type="ZHIPU", model="glm-3-turbo")
    system = '''你是一名辩手，你需要针对一下辩题做辩论
    辩题
    老妈和老婆都掉到水里了，应该先救谁
    你的观点是
    先救老妈
    '''
    
    
    
    debater = Debater(name="test_debater", side="pos", model_config=model_config, system=system)
    resp = debater.debate(history=[])
    print(resp)
    

        
        