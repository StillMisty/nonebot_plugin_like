from nonebot import on_command, get_bots, require
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.log import logger
from asyncio import sleep
import os
import json

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa: E402

__plugin_meta__ = PluginMetadata(
    name="点赞",
    description="给指定QQ点赞",
    type="application",
    usage="赞我 | 一直赞我",
    homepage="https://github.com/StillMisty/nonebot_plugin_like",
)


like = on_command("赞我", priority=5, block=True)

# 定时任务，给所有记录的QQ号点赞
record = on_command("一直赞我", priority=5, block=True)

data_path = "data/nonebot_plugin_like.json"


async def give_like(user_id: int):
    # 给指定QQ号点赞
    bots = get_bots()
    for bot_id, bot in bots.items():
        try:
            for _ in range(5):
                await bot.send_like(user_id=user_id, times=10)
                await sleep(1)
        except ActionFailed as e:
            logger.error(f"给{user_id}点赞失败:{e}")


def get_qq_list() -> set[int]:
    # 获取要的QQ号列表
    if not os.path.exists(data_path):
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, "w") as f:
            json.dump([], f)
            return set()

    with open(data_path, "r") as f:
        try:  # 添加异常处理，防止json文件损坏
            qq_list = json.load(f)
            return set(qq_list)
        except json.JSONDecodeError:
            logger.error(f"{data_path}文件损坏，已重置为空列表")
            return set()


@like.handle()
async def _(event: MessageEvent):
    await give_like(event.user_id)
    await like.finish("已点赞")


@record.handle()
async def _(event: MessageEvent):
    qq_list = get_qq_list()
    qq_list.add(event.user_id)
    with open(data_path, "w") as f:
        json.dump(list(qq_list), f)
    await record.finish("已记录，会每天自动给你点赞哦")


# 定时任务,给所有记录的QQ号点赞
@scheduler.scheduled_job("cron", hour=0, minute=5)
async def give_like_to_all():
    qq_list = get_qq_list()
    for qq in qq_list:
        await give_like(qq)
        logger.info(f"给{qq}点赞")
        await sleep(5)
