import json
import os
import time

import requests

from utils import to_base36, get_tab_id, get_cookies


class InstagramBot:
    def __init__(self, username):
        cookies, csrftoken = get_cookies()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Referer": f"https://www.instagram.com/{username}/",
            "Cookie": cookies,  # 需要加上你自己的 cookie
            "x-csrftoken": csrftoken,
        }
        self.app_id = '936619743392459'
        self.username = username
        self.headers = headers
        self.session = requests.Session()
        self.seq_of_req = 1
        
    def save_json(self, content, name):
        file_path = f'{self.username}/{name}.json'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(content, indent=4))
            
    def get_json(self, name):
        with open(f'{self.username}/{name}.json', "r", encoding="utf-8") as f:
            content = json.loads(f.read())
            return content
            
    def fetch_all_posts(self):
        previous_post_id = ''
        has_next_page = True
        data = []
        count = 0
        while has_next_page:
            previous_post_id, has_next_page, d = self.get_posts(previous_post_id)
            data.extend(d)
            count = count + 1
            print(f'current: {count}')
            time.sleep(0.1)
        self.save_json(data, 'posts')
        
    def get_posts(self, previous_post_id = "") -> ():
        url = "https://www.instagram.com/graphql/query/"
        
        variables = {
            "after": previous_post_id,
            "before": "null",
            "data": {
                "count": 12,
                "include_reel_media_seen_timestamp": "true",
                "include_relationship_info": "true",
                "latest_besties_reel_media": "true",
                "latest_reel_media": "true"
            },
            "first": 12,
            "last": "null",
            "username": self.username,
            "__relay_internal__pv__PolarisIsLoggedInrelayprovider": "true",
            "__relay_internal__pv__PolarisShareSheetV3relayprovider": "true"
        }
        # 表单数据（部分例子字段）
        payload = {
            "__d": "www",
            "__user": "0",  # USER_ID
            "__a": "1",
            "__req": to_base36(self.seq_of_req + 1),  # uniqueRequestID
            "__hs": "20276.HYP:instagram_web_pkg.2.1...0",
            "__rev": "1024473729",  # client revision
            "__s": f"{get_tab_id()}:{get_tab_id()}:74ryvg",
            "variables": json.dumps(variables),
            "server_timestamps": "true",
            "doc_id": "10064872980277354"
        }

        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        # 发出请求
        response = self.session.post(url, headers=headers, data=payload)

        # 输出返回内容
        obj = response.json()['data']['xdt_api__v1__feed__user_timeline_graphql_connection']

        page_info = obj['page_info']
        end_cursor = page_info['end_cursor']
        has_next_page = page_info['has_next_page']
        data = obj['edges']

        return end_cursor, has_next_page, data

    def posts_liked_by_them(self, his_name):
        liked_posts = []
        data = self.get_json('posts')
        for post in data:
            node = post['node']
            code = node['code']
            top_likers = node['top_likers']
            if top_likers:
                print(code)
                print(top_likers)
                print('\n')
                for name in top_likers:
                    if name == his_name:
                        liked_posts.append(post)
        return liked_posts
    
    def fetch_comments_of_all_posts(self):
        data = self.get_json('posts')
        
        all_comments = {}
        
        try:
            count = 0
            for post in data:
                count += 1
                node = post['node']
                code = node['code']
                print(f'({count}/{len(data)})fetching comments for {code}')
                pk = node['pk']
                next_min_id = None
                comments_this_post = []
                for i in range(2):
                    comments, next_min_id = self.get_comments(pk, next_min_id)
                    comments_this_post.extend(comments)
                    time.sleep(0.1)
                    if next_min_id is None:
                        break
                all_comments[code] = comments_this_post
        except Exception as e:
            print(e)
            
        self.save_json(all_comments, 'comments')
    
    def get_comments(self, pk, min_id = None):
        params = f'&min_id={min_id}&sort_order=popular' if min_id else ''
        url = f'https://www.instagram.com/api/v1/media/{pk}/comments/?can_support_threading=true&permalink_enabled=false{params}'
        headers = self.headers.copy()
        headers['x-ig-app-id'] = self.app_id
        response = self.session.get(url, headers=headers)
        obj = response.json()

        comments = obj['comments']
        next_min_id = obj['next_min_id'] if 'next_min_id' in obj else None
        
        return comments, next_min_id
    
    def comments_made_by_them(self, his_name):
        comments = self.get_json("comments")
        for code, comments_in_post in comments.items():
            print(f'{code}:')
            for comment in comments_in_post:
                if comment['user']['username'] == his_name:
                    print(f'{comment['text']}')
                if "preview_child_comments" in comment:
                    comments_preview = comment['preview_child_comments']
                    for cmt in comments_preview:
                        if cmt['user']['username'] == his_name:
                            print(f'{comment['user']['username']}: {comment["text"]}')
                            print(f'\t\t\t{cmt['text']}')
            print('----------------------')    
            
if __name__ == '__main__':
    bot = InstagramBot("stefsunyanzi")
    # bot = InstagramBot("jonahfooddaddy")
    # bot = InstagramBot("janice_students_work")
    
    bot.get_posts()
    # bot.fetch_all_posts()
    # bot.fetch_comments_of_all_posts()
    
    # bot.comments_made_by_them("stefsunyanzi")
    # bot.posts_liked_by_them("stefsunyanzi")