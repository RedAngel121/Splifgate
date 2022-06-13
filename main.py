import discord
import requests
import setup
import json
import asyncio
import math
from discord.ext import tasks
from discord.commands import Option
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}\n----------------------------------")
    update_score.start()
    send_score.start()

"""
@bot.slash_command(guild_ids=[907039631172837457], name="link", description="🎮 Set your Splitgate Gamertag! Make sure your account is connected to discord!")
async def link(ctx: discord.ApplicationContext):
    await ctx.defer()
    # check for role ID on user that initially used the command
    if setup.pc_role_id in [y.id for y in ctx.author.roles]:
        platform = 'steam'
        print("PC true")
    elif setup.xbox_role_id in [y.id for y in ctx.author.roles]:
        platform = 'xbl'
        print("xbox true")
    elif setup.psn_role_id in [y.id for y in ctx.author.roles]:
        platform = 'psn'
        print("psn true")
    else:
        await ctx.respond('Platform Role not selected.')
    if platform != '':
        #get user connected accounts
        profile = await ctx.user.profile(ctx.author)
        accounts = profile.connected_accounts
        print(profile)
        print(accounts)
"""

@bot.slash_command(guild_ids=[907039631172837457], name="set_gamertag", description="🎮 Set your Splitgate Gamertag!")
async def set_gamertag(
    ctx: discord.ApplicationContext,
    platform: Option(str, "Platform", choices=["Steam", "Xbox", "Playstation"], required=True),
    gamertag: Option(str, "Steam Vanity Name, Steam ID, Xbox Gamertag, or PSN Id", required=True)
    ):
    await ctx.defer()
    am = discord.AllowedMentions( users=False )
    if platform == 'Steam':
        r = requests.get(f'https://public-api.tracker.gg/v2/splitgate/standard/search?platform=steam&query={str(gamertag)}', headers={"TRN-Api-Key":setup.trackerkey})
        data = json.loads(r.text)
        try:
            originalgamertag = data['data'][0]['platformUserHandle']
            gamertag = data['data'][0]['platformUserId']
        except:
            await ctx.respond('Gamertag not found!')
            return
    else:
        originalgamertag = gamertag
    with open(os.path.join(__location__, 'data.json'), 'r') as openfile:
        data = json.load(openfile)
    try:
        data[str(ctx.author.id)]
        overwrite = True
    except:
        overwrite = False
    copy = ''
    for a in data:
        platformo = data[a]['platform']
        gamertago = data[a]['gamertag']
        if platformo ==  platform:
            if gamertago == gamertag:
                copy = a
    if copy != '':
        await ctx.respond(f"Sorry, <@{a}> has already set that gamertag", allowed_mentions=am)
    else:
        if (platform == 'Steam'):
            platform = 'steam'
        elif (platform == 'Xbox'):
            platform = 'xbl'
        elif (platform == 'Playstation'):
            platform = 'psn'
        r = requests.get(f'https://public-api.tracker.gg/v2/splitgate/standard/profile/{platform}/{gamertag}', headers={"TRN-Api-Key":setup.trackerkey})
        data_user = json.loads(r.text)
        try:
            data_user['errors']
            working = False
        except:
            working = True
        if (working):
            if (overwrite):
                data[str(ctx.author.id)]['platform'] = platform
                data[str(ctx.author.id)]['gamertag'] = gamertag
                with open(os.path.join(__location__, 'data.json'), "w") as outfile:
                    json.dump(data, outfile, indent=3)
                try: await ctx.author.edit(nick=originalgamertag)
                except: pass
                await ctx.respond(f"Your gamertag has been changed! (Platform: {platform}, Gamertag: {originalgamertag})")
            else:
                new_data = {
                    str(ctx.author.id):{
                    "platform" : platform,
                    "gamertag" : gamertag
                    }
                }
                data.update(new_data)
                with open(os.path.join(__location__, 'data.json'), "w") as outfile:
                    json.dump(data, outfile, indent=3)
                try: await ctx.author.edit(nick=originalgamertag)
                except: pass
                await ctx.respond(f"Set your gamertag to {originalgamertag}!")
        else:
            await ctx.respond(f"Gamertag {gamertag} for the platform {platform} was not found!")

@bot.slash_command(guild_ids=[907039631172837457], name="lookup", description="🔎 Get Your Stats!")
async def lookup(ctx, user: Option(discord.Member, "The user to get information about!", required=True)):
    await ctx.defer()
    with open(os.path.join(__location__, 'data.json'), 'r') as openfile:
        data = json.load(openfile)
    try:
        data[str(user.id)]
        exist = True
    except:
        exist = False
    try:
        if (exist):
            platform = data[str(user.id)]['platform']
            gamertag = data[str(user.id)]['gamertag']
            if data[str(user.id)]['platform'] == 'xbl':
                real_platform = 'Xbox'
            if data[str(user.id)]['platform'] == 'psn':
                real_platform = 'PlayStation'
            if data[str(user.id)]['platform'] == 'steam':
                real_platform = 'Steam'
            r = requests.get(f'https://public-api.tracker.gg/v2/splitgate/standard/profile/{platform}/{gamertag}', headers={"TRN-Api-Key":setup.trackerkey})
            data_user = json.loads(r.text)
            try:
                display_name = data_user['data']['platformInfo']['platformUserHandle']
            except:
                display_name = "I'm broken"
            try:
                current_lvl = data_user['data']['segments'][0]['stats']['progressionLevel']['displayValue']
            except:
                current_lvl = "I'm broken"
            try:
                total_hours = data_user['data']['segments'][0]['stats']['timePlayed']['displayValue']
            except:
                total_hours = "I'm broken"
            try:
                rr = requests.get(f'https://public-api.tracker.gg/v2/splitgate/standard/profile/{platform}/{gamertag}/segments/overview?season={str(setup.season_num)}', headers={"TRN-Api-Key":setup.trackerkey})
                user_data_data = json.loads(rr.content)
                try:
                    season_rank = user_data_data['data'][0]['stats']['rankLevel']['displayValue']
                    season_rank_name = user_data_data['data'][0]['stats']['rankLevel']['metadata']['rankName']
                except:
                    season_rank = ""
                    season_rank_name = "Not Ranked"
                try:
                    season_deaths = user_data_data['data'][0]['stats']['deaths']['value']
                    season_kad = user_data_data['data'][0]['stats']['kad']['value']
                    season_hours = user_data_data['data'][0]['stats']['timePlayed']['displayValue']
                    user_score = ((season_deaths/100)/season_kad)
                    printable_user_score = math.floor(float(user_score) * 100)/100.0
                except:
                    season_deaths = "Unavailable"
                    season_kad = "Unavailable"
                    season_hours = "Unavailable"
                    user_score = "Unavailable"
                    printable_user_score = "Unavailable"
                embed=discord.Embed(title="Information for " + str(user), description=f"**Platform: **{real_platform}\n**User ID/Gamertag:** {display_name}\n**Level:** {current_lvl}\n**Total Hours:** {total_hours}\n\n**Season Hours Played:** {season_hours}\n**Season Rank:** {season_rank} - {season_rank_name}\n**Current Score:** {str(printable_user_score)}")
            except:
                embed=discord.Embed(title="Information for " + str(user), description=f"**Platform: **{real_platform}\n**User ID/Gamertag:** {display_name}\n**Level:** {current_lvl}\n**Total Hours:** {total_hours}")
            if data_user['data']['platformInfo']['avatarUrl'] != None:
                embed.set_thumbnail(url=data_user['data']['platformInfo']['avatarUrl'])
            items = ['kills', 'assists', 'deaths', 'meleeKills', 'killsThruPortal', 'kd']
            for a in items:
                embed.add_field(name=data_user['data']['segments'][0]['stats'][a]['displayName'], value=data_user['data']['segments'][0]['stats'][a]['displayValue'])
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("That user has not set a Splitgate gamertag!")
    except: 
        await ctx.respond("Tracker.gg doesn't have your game stats and info, or there was another error causing this to appear.")

@tasks.loop(seconds=1)
async def update_score():
    guild = bot.get_guild(setup.guild_id)
    team1_score = 0
    team2_score = 0
    team1_channel = await bot.fetch_channel(setup.a_channel)
    team2_channel = await bot.fetch_channel(setup.b_channel)
    with open(os.path.join(__location__, 'data.json'), 'r') as openfile:
        data = json.load(openfile)
    a_role = discord.utils.get(guild.roles, id=setup.a_role_id)
    a_user_ids = [m.id for m in a_role.members]
    b_role = discord.utils.get(guild.roles, id=setup.b_role_id)
    b_user_ids = [m.id for m in b_role.members]
    print(f"{len(a_user_ids) + len(b_user_ids)} users in League")
    for xusers in a_user_ids:
        await asyncio.sleep(30)
        try:
            data[str(xusers)]
            run = True
        except:
            run = False
        if run:
            try:
                platform = data[str(xusers)]['platform']
                gamertag = data[str(xusers)]['gamertag']
                rr = requests.get(f'https://public-api.tracker.gg/v2/splitgate/standard/profile/{platform}/{gamertag}', headers={"TRN-Api-Key":setup.trackerkey})
                data_username = json.loads(rr.text)
                display_name = data_username['data']['platformInfo']['platformUserHandle']
                r = requests.get(f'https://public-api.tracker.gg/v2/splitgate/standard/profile/{platform}/{gamertag}/segments/overview?season={str(setup.season_num)}', headers={"TRN-Api-Key":setup.trackerkey})
                user_data = json.loads(r.content)
                season_deaths = user_data['data'][0]['stats']['deaths']['value']
                season_kad = user_data['data'][0]['stats']['kad']['value']
                user_score = (season_deaths/100)/season_kad
                """ Delete these quotes if they figure out how the points work XD
                try:
                    season_rank = user_data_data['data'][0]['stats']['rankLevel']['value']
                    user_score = user_score + (season_rank/100)
                except: 
                    pass
                """
                printable_user_score = str(math.floor(float(user_score) * 100)/100.0)
                team1_score = team1_score + user_score
                print(f"Team 1 User: {str(display_name)} - Score: {printable_user_score}")
            except Exception as e: 
                user_name = await bot.fetch_user(xusers)
                print(f"Team 1 user: {user_name} not parsable: ", e)
    for xusers in b_user_ids:
        await asyncio.sleep(30)
        try:
            data[str(xusers)]
            heck = data[str(xusers)]
            run = True
        except:
            run = False
        if run:
            try:
                platform = heck['platform']
                gamertag = heck['gamertag']
                rr = requests.get(f'https://public-api.tracker.gg/v2/splitgate/standard/profile/{platform}/{gamertag}', headers={"TRN-Api-Key":setup.trackerkey})
                data_username = json.loads(rr.text)
                display_name = data_username['data']['platformInfo']['platformUserHandle']
                r = requests.get(f'https://public-api.tracker.gg/v2/splitgate/standard/profile/{platform}/{gamertag}/segments/overview?season={str(setup.season_num)}', headers={"TRN-Api-Key":setup.trackerkey})
                user_data = json.loads(r.content)
                season_deaths = user_data['data'][0]['stats']['deaths']['value']
                season_kad = user_data['data'][0]['stats']['kad']['value']
                user_score = (season_deaths/100)/season_kad
                """ Delete these quotes if they figure out how the points work XD
                try:
                    season_rank = user_data_data['data'][0]['stats']['rankLevel']['value']
                    user_score = user_score + (season_rank/100)
                except: 
                    pass
                """
                printable_user_score = str(math.floor(float(user_score) * 100)/100.0)
                team2_score = team2_score + user_score
                print(f"Team 2 User: {str(display_name)} - Score: {printable_user_score}")
            except Exception as e: 
                user_name = await bot.fetch_user(xusers)
                print(f"Team 2 user: {user_name} not parsable: ", e)
    team1_score = str(team1_score).split('.')
    print(team1_score[0])
    await team1_channel.edit(name=f"🟩 TEAM: {team1_score[0]} POINTS")
    team2_score = str(team2_score).split('.')
    print(team2_score[0])
    await team2_channel.edit(name=f"🟦 TEAM: {team2_score[0]} POINTS")

@tasks.loop(seconds=86400)
async def send_score():
    channel = bot.get_channel(setup.r_channel)
    team1_channel = bot.get_channel(setup.a_channel)
    team2_channel = bot.get_channel(setup.b_channel)
    team1_score = team1_channel.name.replace('🟦 TEAM: ', '')
    team2_score = team2_channel.name.replace('🟩 TEAM: ', '')
    team1_score = team1_score.replace(' POINTS', '')
    team2_score = team2_score.replace(' POINTS', '')
    await channel.send(f"**Team 1 Score: **{team1_score}\n**Team 2 Score: **{team2_score}")

bot.run(setup.token)