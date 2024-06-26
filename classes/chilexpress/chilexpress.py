from project.settings.base import env


class Chilexpress:
    serv_code = 'CHILEX'

    # Track
    track_url = env.str(var='CHILEXPRESS_TRACK_URL')

    def __init__(self, *args, **kwargs):
        pass
