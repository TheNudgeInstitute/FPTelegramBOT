import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import common


def get_current_user_name():
    return common.PARTICIPANT_MAP.get(common.PARTICIPANTS[common.CURRENT_PARTICIPANT_INDEX])


def get_current_user_id():
    return common.PARTICIPANTS[common.CURRENT_PARTICIPANT_INDEX]


def publish_game_data():
    try:
        data = {
            'timestamp': datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),
            'user_id': common.PARTICIPANTS[0],
            'n_participants': len(common.PARTICIPANTS)
        }
        common.DB.send_data(data, 'TB_StoryBuilding_Data')
    except:
        traceback.print_exc()
