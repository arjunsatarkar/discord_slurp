import discord

g = lambda obj, attr: getattr(obj, attr, None)
nonerepr = lambda v: repr(v) if v is not None else None


def parse_application(message_application: discord.MessageApplication):
    if message_application is None:
        return None
    return {
        "cover": parse_asset(message_application.cover),
        "description": message_application.description,
        "icon": parse_asset(message_application.icon),
        "id": nonerepr(message_application.id),
        "name": message_application.name,
    }


def parse_asset(asset: discord.Asset):
    if asset is None:
        return None
    return {
        "key": asset.key,
        "url": asset.url,
    }


def parse_attachment(attachment: discord.Attachment):
    return {
        "content_type": attachment.content_type,
        "description": attachment.description,
        "duration": attachment.duration,
        "ephemeral": attachment.ephemeral,
        "filename": attachment.filename,
        "height": attachment.height,
        "id": nonerepr(attachment.id),
        "proxy_url": attachment.proxy_url,
        "size": attachment.size,
        "url": attachment.url,
        "width": attachment.width,
    }


def parse_role_subscription(role_subscription: discord.RoleSubscriptionInfo):
    if role_subscription is None:
        return None
    return {
        "is_renewal": role_subscription.is_renewal,
        "role_subscription_listing_id": nonerepr(
            role_subscription.role_subscription_listing_id
        ),
        "tier_name": role_subscription.tier_name,
        "total_months_subscribed": role_subscription.total_months_subscribed,
    }


def parse_sticker_item(sticker_item: discord.StickerItem):
    return {
        "format": repr(sticker_item.format),
        "id": repr(sticker_item.id),
        "name": sticker_item.name,
        "url": sticker_item.url,
    }


def parse_message_interaction(message_interaction: discord.MessageInteraction):
    if message_interaction is None:
        return None
    return {
        "created_at": int(message_interaction.created_at.timestamp()),
        "id": nonerepr(message_interaction.id),
        "name": message_interaction.name,
        "type": repr(message_interaction.type),
        "user_id": nonerepr(message_interaction.user.id),
    }


async def parse_reaction(reaction: discord.Reaction, max_reaction_users=float("inf")):
    user_ids = []
    i = 0
    async for user in reaction.users():
        if i >= max_reaction_users:
            break
        user_ids.append(repr(user.id))
        i += 1
    return {
        "count": reaction.count,
        "emoji": repr(reaction.emoji),
        "user_ids": user_ids,
    }


async def parse_message(message: discord.Message, max_reaction_users=float("inf")):
    return {
        "activity": message.activity,
        "application": parse_application(message.application),
        "application_id": nonerepr(message.application_id),
        "attachments": [
            parse_attachment(attachment) for attachment in message.attachments
        ],
        "author_id": nonerepr(g(message.author, "id")),
        "channel_id": nonerepr(g(message.channel, "id")),
        "content": message.content or message.system_content,
        "created_at": int(message.created_at.timestamp()),
        "edited_at": (
            int(message.edited_at.timestamp())
            if message.edited_at is not None
            else None
        ),
        "embeds": [embed.to_dict() for embed in message.embeds],
        "flags": repr(message.flags),
        "guild_id": nonerepr(g(message.guild, "id")),
        "id": nonerepr(message.id),
        "interaction": parse_message_interaction(message.interaction),
        "mention_everyone": message.mention_everyone,
        "pinned": message.pinned,
        "position": message.position,
        "raw_mentions": message.raw_mentions,
        "raw_role_mentions": message.raw_role_mentions,
        "reactions": [
            await parse_reaction(reaction, max_reaction_users)
            for reaction in message.reactions
        ],
        "reference": nonerepr(g(message.reference, "id")),
        "role_subscription": parse_role_subscription(message.role_subscription),
        "stickers": [
            parse_sticker_item(sticker_item) for sticker_item in message.stickers
        ],
        "tts": message.tts,
        "type": repr(message.type),
        "webhook_id": nonerepr(message.webhook_id),
    }
