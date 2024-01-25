#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/01/25 10:58:33
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

from typing import List

from agent import LOG_DIR, Claim, Debater, Judger, Message
from snippets.logs import get_file_log

logger = get_file_log(name=__name__, log_dir=LOG_DIR)

class ModelBBGame:
    def __init__(self, 
                 topic:str,
                 pos_claim:str,
                 pos_debaters:List[Debater],
                 neg_claim:str,
                 neg_debaters:List[Debater],
                 judgers:List[Judger]) -> None:
        self.topic = topic
        self.pos_claim = Claim(side="正方", content=pos_claim)
        self.neg_claim =  Claim(side="反方", content=neg_claim)
        self.pos_debaters = pos_debaters
        self.neg_debaters = neg_debaters
        self.judgers = judgers
    
    def run(self):
        logger.info("Model BB game Begin!")
        logger.info(f"Topic is : {self.topic}")
        logger.info(f"Positive side claim is:{self.pos_claim}")
        logger.info(f"Positive side debaters are:{self.pos_debaters}")
        logger.info(f"Negative side claim is:{self.neg_claim}")
        logger.info(f"Negative side debaters are:{self.neg_debaters}")
        logger.info(f"Judgers are :{self.judgers}")
        assert len(self.pos_debaters) == len(self.neg_debaters)
        history = []
        system_pattern = '''你是一名辩手，你需要针对一下辩题做辩论
        辩题
        {topic}
        你的观点是
        {claim}
        '''
        
        for _round in range(0, len(self.pos_debaters)):
            logger.info(f"round :{_round+1}")
            
            debater = self.pos_debaters[_round]
            logger.info(f"{debater}[{self.pos_claim.content}] talk:")
            resp = debater.debate(claim=self.pos_claim, system=system_pattern.format(topic=self.topic, claim=self.pos_claim), history=history)
            logger.info(f"{debater}'s talk:\n{resp}")
            history.append(Message(claim=self.pos_claim, name=debater.name, content=resp))
            logger.info("*"*50)
            
            
            debater = self.neg_debaters[_round]
            logger.info(f"{debater}[{self.neg_claim.content}] talk:")
            resp = debater.debate(claim=self.neg_claim, system=system_pattern.format(topic=self.topic, claim=self.neg_claim), history=history)
            logger.info(f"{debater}'s talk:\n{resp}")
            history.append(Message(claim=self.neg_claim, name=debater.name, content=resp))
            logger.info("*"*50)

            
        logger.info("start to judge")
        for judger in self.judgers:
            judge_rs = judger.judge(topic=self.topic, pos_claim=self.pos_claim, neg_claim=self.neg_claim, history=history)
            logger.info(f"{judger.name} judge result:\n{judge_rs}")
            logger.info("*"*50)


            
        
        logger.info("Model BB game End")
    
    
    
if __name__ == "__main__":
    debater1 = Debater("debater1-glm3-turbo", model_config = dict(model_type="ZHIPU", model="glm-3-turbo"))
    debater2 = Debater("debater2-glm3-turbo", model_config = dict(model_type="ZHIPU", model="glm-3-turbo"))
    debater3 = Debater("debater3-glm4", model_config = dict(model_type="ZHIPU", model="glm-4"))
    debater4 = Debater("debater4-glm4", model_config = dict(model_type="ZHIPU", model="glm-4"))

    
    
    judge1 = Judger("judger1-glm3-turbo",model_config = dict(model_type="ZHIPU", model="glm-3-turbo") )
    judge2 = Judger("judger2-glm4",model_config = dict(model_type="ZHIPU", model="glm-3-turbo") )

    
    game = ModelBBGame(
                 topic="老妈和老婆一起掉到水里了，你先救谁?",
                 pos_claim="先救老妈",
                 pos_debaters=[debater1,debater2],
                 neg_claim="先救老婆",
                 neg_debaters=[debater3,debater4],
                 judgers=[judge1,judge2]) 
    
    game.run()
    
    

