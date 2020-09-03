import sys

import gym
import numpy as np
import gym.spaces


class MyEnv(gym.Env):
    metadata = {'render.modes': ['human', 'ansi']}
    FIELD_TYPES = [
        'S',  # 0: �X�^�[�g
        'G',  # 1: �S�[��
        '~',  # 2: �Ő�(�G�̌����m��1/10)
        'w',  # 3: �X(�G�̌����m��1/2)
        '=',  # 4: �ŏ�(1step����1�̃_���[�W, �G�̌����m��1/2)
        'A',  # 5: �R(�����Ȃ�)
        'Y',  # 6: �E��
    ]
    MAP = np.array([
        [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],  # "AAAAAAAAAAAA"
        [5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],  # "AA~~~~~~~~~~"
        [5, 5, 2, 0, 2, 2, 5, 2, 2, 4, 2, 2],  # "AA~S~~A~~=~~"
        [5, 2, 2, 2, 2, 2, 5, 5, 4, 4, 2, 2],  # "A~~~~~AA==~~"
        [2, 2, 3, 3, 3, 3, 5, 5, 2, 2, 3, 3],  # "~~wwwwAA~~ww"
        [2, 3, 3, 3, 3, 5, 2, 2, 1, 2, 2, 3],  # "~wwwwA~~G~~w"
        [2, 2, 2, 2, 2, 2, 4, 4, 2, 2, 2, 2],  # "~~~~~~==~~~~"
    ])
    MAX_STEPS = 100

    def __init__(self):
        super().__init__()
        # action_space, observation_space, reward_range ��ݒ肷��
        self.action_space = gym.spaces.Discrete(4)  # ������k
        self.observation_space = gym.spaces.Box(
            low=0,
            high=len(self.FIELD_TYPES),
            shape=self.MAP.shape
        )
        self.reward_range = [-1., 100.]
        self._reset()

    def _reset(self):
        # ���X�̕ϐ�������������
        self.pos = self._find_pos('S')[0]
        self.goal = self._find_pos('G')[0]
        self.done = False
        self.damage = 0
        self.steps = 0
        return self._observe()

    def _step(self, action):
        # 1�X�e�b�v�i�߂鏈�����L�q�B�߂�l�� observation, reward, done(�Q�[���I��������), info(�ǉ��̏��̎���)
        if action == 0:
            next_pos = self.pos + [0, 1]
        elif action == 1:
            next_pos = self.pos + [0, -1]
        elif action == 2:
            next_pos = self.pos + [1, 0]
        elif action == 3:
            next_pos = self.pos + [-1, 0]

        if self._is_movable(next_pos):
            self.pos = next_pos
            moved = True
        else:
            moved = False

        observation = self._observe()
        reward = self._get_reward(self.pos, moved)
        self.damage += self._get_damage(self.pos)
        self.done = self._is_done()
        return observation, reward, self.done, {}

    def _render(self, mode='human', close=False):
        # human �̏ꍇ�̓R���\�[���ɏo�́Bansi�̏ꍇ�� StringIO ��Ԃ�
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        outfile.write('\n'.join(' '.join(
                self.FIELD_TYPES[elem] for elem in row
                ) for row in self._observe()
            ) + '\n'
        )
        return outfile

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self, pos, moved):
        # ��V��Ԃ��B��V�̗^������������A�����ł�
        # - �S�[���ɂ��ǂ蒅���� 100 �|�C���g
        # - �_���[�W�̓S�[�����ɂ܂Ƃ߂Čv�Z
        # - 1�X�e�b�v���Ƃ�-1�|�C���g(�ł��邾���Z���X�e�b�v�ŃS�[���ɂ��ǂ蒅������)
        # �Ƃ���
        if moved and (self.goal == pos).all():
            return max(100 - self.damage, 0)
        else:
            return -1

    def _get_damage(self, pos):
        # �_���[�W�̌v�Z
        field_type = self.FIELD_TYPES[self.MAP[tuple(pos)]]
        if field_type == 'S':
            return 0
        elif field_type == 'G':
            return 0
        elif field_type == '~':
            return 10 if np.random.random() < 1/10. else 0
        elif field_type == 'w':
            return 10 if np.random.random() < 1/2. else 0
        elif field_type == '=':
            return 11 if np.random.random() < 1/2. else 1

    def _is_movable(self, pos):
        # �}�b�v�̒��ɂ��邩�A�����Ȃ��ꏊ�ɂ��Ȃ���
        return (
            0 <= pos[0] < self.MAP.shape[0]
            and 0 <= pos[1] < self.MAP.shape[1]
            and self.FIELD_TYPES[self.MAP[tuple(pos)]] != 'A'
        )

    def _observe(self):
        # �}�b�v�ɗE�҂̈ʒu���d�˂ĕԂ�
        observation = self.MAP.copy()
        observation[tuple(self.pos)] = self.FIELD_TYPES.index('Y')
        return observation

    def _is_done(self):
        # ����͍ő�� self.MAX_STEPS �܂łƂ���
        if (self.pos == self.goal).all():
            return True
        elif self.steps > self.MAX_STEPS:
            return True
        else:
            return False

    def _find_pos(self, field_type):
        return np.array(list(zip(*np.where(
        self.MAP == self.FIELD_TYPES.index(field_type)
    ))))