import json
import re
import discord
import io
from redbot.core import commands

class SNBT(commands.Cog):
    """Convert between JSON and SNBT (Minecraft's Stringified NBT format)"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def snbt(self, ctx):
        """Base command for SNBT conversions"""
        pass

    @snbt.command(name="fromjson")
    @commands.bot_has_permissions(embed_links=True)
    async def fromjson(self, ctx, *, json_input: str = None):
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

    @snbt.command(name="tojson")
    @commands.bot_has_permissions(embed_links=True)
    async def tojson(self, ctx, *, snbt_input: str = None):
        """
        Convert SNBT to JSON
        
        You can either:
        - Paste SNBT in a code block (```snbt [...] ```)
        - Attach a .snbt file
        """
        # Check for attachments first
        if ctx.message.attachments:
            file = ctx.message.attachments[0]
            snbt_text = (await file.read()).decode('utf-8')
        else:
            if not snbt_input:
                await ctx.send_help()
                return
            # Clean code block formatting
            snbt_text = re.sub(r'```(?:snbt)?\n?|\n?```', '', snbt_input).strip()

        try:
            json_result = self.snbt_to_json(snbt_text)
        except Exception as e:
            await ctx.send(f"Error during conversion: {str(e)}")
            return

        # Format output as JSON code block
        if len(json_result) > 1900:
            await ctx.send("Result too long - sending as file:", 
                          file=discord.File(io.StringIO(json_result), "result.json"))
        else:
            await ctx.send(f"```json\n{json_result}\n```")

    def convert_string(self, s):
        """Helper function to escape strings using double quotes"""
        s = s.replace('\\', '\\\\')
        return '"' + s.replace('"', '\\"') + '"'

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
            # Detect and convert JSON-in-string
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

    def snbt_to_json(self, snbt_str):
        """
        Convert SNBT to JSON by quoting unquoted keys and replacing single quotes.
        
        Note: This implementation makes a best-effort attempt and assumes the SNBT is in a relatively
        simple format.
        """
        # Regex to match unquoted keys (after '{' or ',' and optional whitespace)
        pattern = r'([{\s,])([a-zA-Z0-9_]+)\s*:'
        replaced = re.sub(pattern, r'\1"\2":', snbt_str)
        # Replace single quotes with double quotes
        replaced = replaced.replace("'", '"')
        try:
            data = json.loads(replaced)
            return json.dumps(data, indent=4)
        except Exception as e:
            raise ValueError("Invalid SNBT format") from e
