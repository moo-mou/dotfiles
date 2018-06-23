import os
import io
import json

import requests

from m_base import Base
from util import m_path

SAMPLE_RATE = 16000


class Voixdb(Base):
    def __init__(self):
        super().__init__([
            'm_audio.ass',
            'm_audio.audio_util',
            'pydub',
            'librosa',
        ])

    def _process(self, dir, dataset_id, server, svc):
        librosa = self._module('librosa')

        for f in os.listdir(dir):
            if f.endswith('mp3'):
                ytid, spkid, start_time, end_time = f[:-4].split('~')
                data, sr = librosa.core.load(
                    os.path.join(dir, f),
                    sr=SAMPLE_RATE,
                    duration=30,
                    mono=True)

                # skip '[' and ']'
                file = io.BytesIO(
                    json.dumps(data.tolist())[1:-1].encode('utf-8'))

                result = requests.post(
                    server + '/%s/%s/%s' % (svc, dataset_id, spkid),
                    files={
                        'bin': file,
                    },
                    data={'meta': json.dumps({
                        'sr': SAMPLE_RATE,
                    })})

    def identify(self, dir, dataset_id='0', server='http://localhost:5000'):
        return self._process(dir, dataset_id, server, 'identify')

    def register(self, dir, dataset_id='0', server='http://localhost:5000'):
        '''
        Given a data dir prepared by m_audio.gather_youtube_segments, register these
        voixdb instance.
        '''
        return self._process(dir, dataset_id, server, 'register')