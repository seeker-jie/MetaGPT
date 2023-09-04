#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/6/5 01:44
@Author  : alexanderwu
@File    : skill_manager.py
@Modified By: mashenquan, 2023/8/20. Remove useless `_llm`
"""
from metagpt.actions import Action
from metagpt.const import PROMPT_PATH
from metagpt.document_store.chromadb_store import ChromaStore
from metagpt.logs import logger

Skill = Action


class SkillManager:
    """用来管理所有技能
       to manage all skills
    """

    def __init__(self):
        self._store = ChromaStore('skill_manager')
        self._skills: dict[str: Skill] = {}

    def add_skill(self, skill: Skill):
        """
        增加技能，将技能加入到技能池与可检索的存储中
        Adding skills, adding skills to skill pools and retrievable storage
        :param skill: 技能 Skill
        :return:
        """
        self._skills[skill.name] = skill
        self._store.add(skill.desc, {}, skill.name)

    def del_skill(self, skill_name: str):
        """
        删除技能，将技能从技能池与可检索的存储中移除
        delete skill removes skill from skill pool and retrievable storage
        :param skill_name: 技能名 skill name
        :return:
        """
        self._skills.pop(skill_name)
        self._store.delete(skill_name)

    def get_skill(self, skill_name: str) -> Skill:
        """
        通过技能名获得精确的技能
         Get the exact skill by skill name
        :param skill_name: 技能名 skill name
        :return: 技能 Skill
        """
        return self._skills.get(skill_name)

    def retrieve_skill(self, desc: str, n_results: int = 2) -> list[Skill]:
        """
        通过检索引擎获得技能 Acquiring Skills Through Search Engines
        :param desc: 技能描述 skill description
        :return: 技能（多个）skill(s)
        """
        return self._store.search(desc, n_results=n_results)['ids'][0]

    def retrieve_skill_scored(self, desc: str, n_results: int = 2) -> dict:
        """
        通过检索引擎获得技能 Acquiring Skills Through Search Engines
        :param desc: 技能描述 skill description
        :return: 技能与分数组成的字典 A dictionary of skills and scores
        """
        return self._store.search(desc, n_results=n_results)

    def generate_skill_desc(self, skill: Skill) -> str:
        """
        为每个技能生成对应的描述性文本 Generate corresponding descriptive text for each skill
        :param skill:
        :return:
        """
        path = PROMPT_PATH / "generate_skill.md"
        text = path.read_text()
        logger.info(text)


if __name__ == '__main__':
    manager = SkillManager()
    manager.generate_skill_desc(Action())
