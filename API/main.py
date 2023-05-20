import argparse

import vk_api
from tabulate import tabulate

from config import TOKEN


class VkApi:
    def __init__(self, user_id):
        self.user_id = user_id
        self.vk_session = vk_api.VkApi(token=TOKEN)

    def get_user_status(self):
        status = self.vk_session.method("status.get", {"user_id": self.user_id})
        print(f'Status: {status["text"]}')

    def get_user_name(self, other_user_id):
        user = self.vk_session.method("users.get", {"user_ids": other_user_id})
        return user[0]['first_name'], user[0]['last_name']

    def get_friends_list(self):
        output = list(list())
        friends = self.vk_session.method("friends.get", {"user_id": self.user_id})
        print('Friends:')
        for friend in friends["items"]:
            row = [
                friend,
                self.get_user_name(friend)[0],
                self.get_user_name(friend)[1]
            ]
            output.append(row)
        print(tabulate(output, headers=['id', 'Name', 'Last_Name']))

    def get_albums_names(self):
        albums = self.vk_session.method("photos.getAlbums", {"owner_id": self.user_id})
        print('Albums name:')
        for name_album in albums["items"]:
            print(name_album['title'])

    def get_followers(self):
        output = list(list())
        followers = self.vk_session.method("users.getFollowers", {"user_id": self.user_id})
        print("Followers:")
        for follower in followers["items"]:
            row = [
                follower,
                self.get_user_name(follower)[0],
                self.get_user_name(follower)[1]
            ]
            output.append(row)
        print(tabulate(output, headers=['id', 'Name', 'Last_Name']))

    def get_groups(self):
        output = list(list())
        groups = self.vk_session.method("groups.get", {"user_id": self.user_id})
        print("Groups name:")
        for group in groups["items"]:
            group_info = self.vk_session.method("groups.getById", {"group_id": group})
            row = [group,
                   group_info[0]['name'],
                   group_info[0]['screen_name']]
            output.append(row)
        print(tabulate(output, headers=['id', 'Name', 'Screen_name']))


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
    parser.add_argument(
        '-s',
        '--status',
        action="store_true",
        help='user status'
    )
    parser.add_argument(
        '-a',
        '--albums',
        action="store_true",
        help='albums names'
    )
    args = parser.parse_args()

    vk = VkApi(args.userId)
    if args.friends:
        vk.get_friends_list()
    if args.followers:
        vk.get_followers()
    if args.groups:
        vk.get_groups()
    if args.status:
        vk.get_user_status()
    if args.albums:
        vk.get_albums_names()


if __name__ == '__main__':
    main()
