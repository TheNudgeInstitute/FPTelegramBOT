import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import common


def get_current_user_name():
    return common.PARTICIPANT_MAP.get(common.PARTICIPANTS[common.CURRENT_PARTICIPANT_INDEX])


def get_current_user_id():
    return common.PARTICIPANTS[common.CURRENT_PARTICIPANT_INDEX]


def publish_game_data(success: bool):
    try:
        timestamp = datetime.now(ZoneInfo('Asia/Kolkata'))
        data = {
            'timestamp': timestamp.isoformat(),
            'date': timestamp.strftime('%Y-%m-%d'),
            'user_id': common.PARTICIPANTS[0],
            'n_participants': len(common.PARTICIPANTS),
            'success': success,
            'participants': ','.join(map(str, common.PARTICIPANTS))
        }
        common.DB.send_data(data)
    except:
        traceback.print_exc()
