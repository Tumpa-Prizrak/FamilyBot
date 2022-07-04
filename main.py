import helper as h
import discord, time, aeval
from discord.ext import commands

bot = commands.Bot(command_prefix=h.json_data["prefix"], intents=discord.Intents.all())

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user):
    if reaction.message.id == h.json_data["reaction_role"]["message"]:
        if reaction.emoji not in h.json_data["reaction_role"]["roles"].keys():
            await reaction.remove(user)
        await user.add_roles(user.guild.get_role(h.json_data["reaction_role"]["roles"][reaction.emoji]))
    h.create_log(f"{user} add reaction {reaction.emoji} to the message {reaction.message.id}", "TRACE")

@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.message.id == h.json_data["reaction_role"]["message"]:
        if reaction.emoji not in h.json_data["reaction_role"]["roles"].keys():
            await reaction.remove(user)         
        await user.remove_roles(user.guild.get_role(h.json_data["reaction_role"]["roles"][reaction.emoji]))
    h.create_log(f"{user} removed reaction {reaction.emoji} from the message {reaction.message.id}", "TRACE")


@bot.command(aliases=['eval', 'aeval', 'evaluate', 'выполнить', 'exec', 'execute', 'code'])
async def __eval(ctx, *, content):
    await ctx.message.delete()
    if ctx.author.id not in h.json_data['owners']:
        return await ctx.send("Nope")
    code = "\n".join(content.split("\n")[1:])[:-3] if content.startswith("```") and content.endswith("```") else content
    standard_args = {
        "bot": bot,
        "ctx": ctx
    }
    start = time.time()  # import time, для расчёта времени выполнения
    try:
        r = await aeval.aeval(f"""{code}""", standard_args, {})  # выполняем код
        ended = time.time() - start  # рассчитываем конец выполнения
        if not code.startswith('#nooutput'):
            # Если код начинается с #nooutput, то вывода не будет
            embed = discord.Embed(title="Успешно!", description=f"Выполнено за: {ended}", color=0x99ff99)
            embed.add_field(name=f'Входные данные:', value=f'`{h.minify_text(str(code))}`')
            embed.add_field(name=f'Выходные данные:', value=f'`{h.minify_text(str(r))}`', inline=False)
            await ctx.send(embed=embed)
    except Exception as e:
        ended = time.time() - start
        code = h.minify_text(str(code))
        embed = discord.Embed(title=f"При выполнении возникла ошибка.\nВремя: {ended}",
                              description=f'Ошибка:\n```py\n{e}```', color=0xff0000)
        embed.add_field(name=f'Входные данные:', value=f'`{h.minify_text(str(code))}`', inline=False)
        await ctx.send(embed=embed)
        raise e

bot.start(h.json_dats["prefix"])