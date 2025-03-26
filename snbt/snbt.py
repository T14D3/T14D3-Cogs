import json
import re
import discord
import io
from redbot.core import commands

class SNBT(commands.Cog):
    """Convert JSON to SNBT (Minecraft's Stringified NBT format)"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def jsontosnbt(self, ctx, *, json_input: str = None):
        """
        Convert JSON to SNBT (Minecraft's Stringified NBT format)
        
        You can either:
        - Paste JSON in a code block (```json [...] ```)
        - Attach a .json file
        """
        # Check for attachments first
        if ctx.message.attachments:
            file = ctx.message.attachments[0]
            if not file.filename.endswith('.json'):
                await ctx.send("Please upload a .json file!")
                return
            json_text = (await file.read()).decode('utf-8')
        else:
            if not json_input:
                await ctx.send_help()
                return
            
            # Clean code block formatting
            json_text = re.sub(r'```(?:json)?\n?|\n?```', '', json_input).strip()

        try:
            # Parse JSON
            data = json.loads(json_text)
            # Convert to SNBT
            snbt_result = self.json_to_snbt(data)
        except json.JSONDecodeError:
            await ctx.send("Invalid JSON format! Please check your input.")
            return
        except Exception as e:
            await ctx.send(f"Error during conversion: {str(e)}")
            return

        # Format output
        if len(snbt_result) > 1900:
            await ctx.send("Result too long - sending as file:", 
                          file=discord.File(io.StringIO(snbt_result), "result.snbt"))
        else:
            await ctx.send(f"```snbt\n{snbt_result}\n```")

    def convert_string(self, s):
        """Helper function to escape strings"""
        s = s.replace('\\', '\\\\')
        num_single = s.count("'")
        num_double = s.count('"')
        if num_single <= num_double:
            return f"'{s.replace("'", "\\'")}'"
        return f'"{s.replace('"', '\\"')}"'

    def json_to_snbt(self, obj):
        """Recursive conversion with JSON-in-string detection"""
        if isinstance(obj, dict):
            pairs = []
            for k, v in obj.items():
                key = k if re.fullmatch(r'^[a-zA-Z0-9_]+$', k) else self.convert_string(k)
                pairs.append(f"{key}:{self.json_to_snbt(v)}")
            return "{" + ",".join(pairs) + "}"
        elif isinstance(obj, list):
            return "[" + ",".join(self.json_to_snbt(e) for e in obj) + "]"
        elif isinstance(obj, str):
            # Detect and convert JSON-in-strings
            if (obj.startswith('{') and obj.endswith('}')) or (obj.startswith('[') and obj.endswith(']')):
                try:
                    parsed = json.loads(obj)
                    return self.json_to_snbt(parsed)
                except json.JSONDecodeError:
                    pass
            return self.convert_string(obj)
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        elif obj is None:
            return "null"
        elif isinstance(obj, (int, float)):
            return str(int(obj)) if isinstance(obj, float) and obj.is_integer() else str(obj)
        else:
            raise TypeError(f"Unsupported type: {type(obj)}")