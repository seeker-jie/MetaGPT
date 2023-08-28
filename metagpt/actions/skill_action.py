import ast
import importlib

from metagpt.actions import Action, ActionOutput
from metagpt.learn.skill_loader import Skill
from metagpt.logs import logger


class ArgumentsParingAction(Action):
    def __init__(self, options, last_talk: str, skill: Skill, context=None, llm=None, **kwargs):
        super(ArgumentsParingAction, self).__init__(options=options, name='', context=context, llm=llm)
        self.skill = skill
        self.ask = last_talk
        self.rsp = None
        self.args = None

    @property
    def prompt(self):
        prompt = f"{self.skill.name} function parameters description:\n"
        for k, v in self.skill.arguments.items():
            prompt += f"parameter `{k}`: {v}\n"
        prompt += "\n"
        prompt += "Examples:\n"
        for e in self.skill.examples:
            prompt += f"If want you to do `{e.ask}`, return `{e.answer}` brief and clear.\n"
        prompt += f"\nNow I want you to do `{self.ask}`, return in examples format above, brief and clear."
        return prompt

    async def run(self, *args, **kwargs) -> ActionOutput:
        prompt = self.prompt
        logger.info(prompt)
        rsp = await self.llm.aask(msg=prompt, system_msgs=[])
        logger.info(rsp)
        self.args = ArgumentsParingAction.parse_arguments(skill_name=self.skill.name, txt=rsp)
        self.rsp = ActionOutput(content=rsp)
        return self.rsp

    @staticmethod
    def parse_arguments(skill_name, txt) -> dict:
        prefix = skill_name + "("
        if prefix not in txt:
            logger.error(f"{skill_name} not in {txt}")
            return None
        if ")" not in txt:
            logger.error(f"')' not in {txt}")
            return None
        begin_ix = txt.find(prefix)
        end_ix = txt.rfind(")")
        args_txt = txt[begin_ix + len(prefix): end_ix]
        logger.info(args_txt)
        fake_expression = f"dict({args_txt})"
        parsed_expression = ast.parse(fake_expression, mode='eval')
        args = {}
        for keyword in parsed_expression.body.keywords:
            key = keyword.arg
            value = ast.literal_eval(keyword.value)
            args[key] = value
        return args


class SkillAction(Action):
    def __init__(self, options, skill: Skill, args: dict, context=None, llm=None, **kwargs):
        super(SkillAction, self).__init__(options=options, name='', context=context, llm=llm)
        self._skill = skill
        self._args = args
        self.rsp = None

    async def run(self, *args, **kwargs) -> str | ActionOutput | None:
        """Run action"""
        self.rsp = self.find_and_call_function(self._skill.name, args=self._args, **self.options)
        return ActionOutput(content=self.rsp, instruct_content=self._skill.json())

    @staticmethod
    def find_and_call_function(function_name, args, **kwargs):
        try:
            module = importlib.import_module("metagpt.learn")
            function = getattr(module, function_name)
            # 调用函数并返回结果
            result = function(**args, **kwargs)
            return result
        except (ModuleNotFoundError, AttributeError):
            logger.error(f"{function_name} not found")
            return None


if __name__ == '__main__':
    ArgumentsParingAction.parse_arguments(skill_name="text_to_image",
                                          txt='`text_to_image(text="Draw an apple", size_type="512x512")`')