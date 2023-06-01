import argparse

import requests
from tabulate import tabulate

from config import TOKEN


class VkApi:
    def __init__(self, user_id):
        self.user_id = user_id
        self.token = TOKEN

    def get_user_info(self, user_id):

        req = requests.get("https://api.vk.com/method/users.get?",
                           params={
                                'access_token': self.token,
                                'user_id': user_id,
                                'v': 5.131
                            }).json()
        info = req["response"][0]
        return info['id'], info['first_name'], info['last_name']

    def get_friends_list(self):
        friends_req = requests.get("https://api.vk.com/method/friends.get?",
                                   params={
                                       'access_token': self.token,
                                       'user_id': self.user_id,
                                       'v': 5.131
                                   }).json()['response']
        print('Friends:')
        self.print_table(friends_req)

    def get_followers(self):
        followers_req = requests.get("https://api.vk.com/method/users.getFollowers?",
                                     params={
                                         'access_token': self.token,
                                         'user_id': self.user_id,
                                         'v': 5.131
                                     }).json()['response']
        print("Followers:")
        self.print_table(followers_req)

    def get_groups(self):
        output = list(list())
        groups_req = requests.get("https://api.vk.com/method/groups.get?",
                                  params={
                                      'access_token': self.token,
                                      'group_id': self.user_id,
                                      'v': 5.131
                                  }).json()['response']
        print("Groups name:")
        for group in groups_req["items"]:
            group_info = requests.get("https://api.vk.com/method/groups.getById?", params={
                'access_token': self.token,
                'group_id': group,
                'v': 5.131
            }).json()['response'][0]
            row = [
                group_info['id'],
                group_info['name'],
                group_info['screen_name'],
            ]
            output.append(row)
        print(tabulate(output, headers=['id', 'name', 'screen_name']))

    def print_table(self, req_info):
        output = list(list())
        for item in req_info["items"]:
            row = [
                item,
                self.get_user_info(item)[1],
                self.get_user_info(item)[2]
            ]
            output.append(row)
        print(tabulate(output, headers=['id', 'Name', 'Last_Name']))

# 284104706
# 242423755
def main():
    parser = argparse.ArgumentParser(description='Using the Vk API')
    parser.add_argument(
        '-i',
        '--userId',
        type=int,
        help='user id of which you need information'
    )
    parser.add_argument(
        '-f',
        '--friends',
        action="store_true",
        help='user friends list print'
    )
    parser.add_argument(
        '-l',
        '--followers',
        action="store_true",
        help='user followers list print'
    )
    parser.add_argument(
        '-g',
        '--groups',
        action="store_true",
        help='user groups list print'
    )
    args = parser.parse_args()

    vk = VkApi(args.userId)
    if args.friends:
        vk.get_friends_list()
    if args.followers:
        vk.get_followers()
    if args.groups:
        vk.get_groups()


if __name__ == '__main__':
    main()
