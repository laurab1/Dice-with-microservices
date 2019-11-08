from email.message import EmailMessage

from flask import current_app as app

from monolith.database import Story


def story_digest(story):
    '''
    Returns a textual representation of a given story, meant to be sent
    via mail digest.
    '''
    roll = ', '.join(story.dice_set)
    name = f'{story.author.firstname} {story.author.lastname}'
    return (
        f'author: {name} ({story.author.username})\n'
        f'roll: {roll}\n'
        f'date: {story.date}\n'
        f'story: {story.text}\n'
        f'likes: {story.likes} -- dislikes: {story.dislikes}\n'
    )


def build_user_digest(user, date_from, date_to):
    '''
    Builds a complete email digest for a given user and a given time
    interval.

    Args:
        user(User): the user requesting the service
        date_from(date)/date_to(date): determine the time frame of the digest
    
    Returns:
        msg: message to be sent via e-mail
    '''
    msg = EmailMessage()
    msg['Subject'] = f'Storyteller digest from {date_from} to {date_to}'
    msg['From'] = app.config['SERVER_MAIL']
    msg['To'] = user.email

    if len(user.follows) == 0:
        msg.set_content('Start following your favourite users to get '
                        'periodic digests.')
        return msg

    followed_ids = [u.id for u in user.follows]
    stories = Story.query.filter(Story.author_id.in_(followed_ids)) \
                         .filter(Story.date >= date_from) \
                         .filter(Story.date <= date_to) \
                         .filter_by(deleted=False) \
                         .filter_by(is_draft=False) \
                         .order_by(Story.date.desc()).all()
    if stories != []:
        msg.set_content('----------\n'.join(story_digest(s) for s in stories))
        return msg

    msg.set_content('No stories uploaded from your following.')
    return msg
