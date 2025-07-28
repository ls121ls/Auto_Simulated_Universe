    def get_text_type(self, text, types, prefix=1):
        for i in types:
            if i[:prefix] in text:
                return i
        return None
    
    def test(self):
        self.find_team_member()


    def find_team_member(self):
        boxes = [[1620, 1790, 289, 335],[1620, 1790, 384, 427],[1620, 1790, 478, 521],[1620, 1790, 570, 618]]
        team_member = {}
        for i,b in enumerate(boxes):
            name = self.clean_text(self.ts.ocr_one_row(self.get_screen(), b))
            if name in self.character_prior:
                team_member[name] = i
        return team_member

    def get_now_area(self, deep=0):
        team_member = self.find_team_member()
        self.area_text = self.clean_text(self.ts.ocr_one_row(self.screen, [50, 350, 3, 35]), char=0)
        print('area_text:', self.area_text, 'deep:', deep)
        if '位面' in self.area_text or '区域' in self.area_text or '第' in self.area_text:
            check_ok = 1
            for i in team_member:
                if i not in self.team_member or team_member[i] != self.team_member[i]:
                    check_ok = 0
                    break

            if not check_ok:
                self.team_member = team_member
                print('team_member:', team_member)
                for i in self.team_member:

                    # 从当前队伍中,选取处于内置远程角色列表中的第一个远程角色
                    if i in config.long_range_list:
                        self.long_range = str(self.team_member[i]+1) # 更新默认远程角色
                        break

            res = self.get_text_type(self.area_text, ['事件', '奖励', '遭遇', '商店', '首领', '战斗', '财富', '休整', '位面'], prefix=2)            
            if (res == '位面' or res is None) and deep == 0:
                self.mouse_move(20)
                scr = self.screen
                time.sleep(0.3)
                self.get_screen()
                self.mouse_move(-20)
                res = self.get_now_area(deep=1)
                self.screen = scr
            return res
        else:
            return None
    
    def find_portal(self, type=None):
        prefer_portal = {'奖励':3, '战斗':3, '事件':1, '遭遇':1, '商店':2, '财富':2}
        if self.speed:
            prefer_portal = {'商店':3, '财富':3, '奖励':2, '事件':2, '战斗':1, '遭遇':1}
            if self.quan and self.allow_e:
                prefer_portal['战斗'] = 2
        if config.enable_portal_prior:
            prefer_portal.update(config.portal_prior)
        prefer_portal.update({'首领':4, '休整':4})
        tm = time.time()
        text = self.ts.find_with_box([0,1920,0,540], forward=1, mode=2)
        portal = {'score':0,'nums':0,'type':''}
        for i in text:
            if ('区' in i['raw_text'] or '域' in i['raw_text']) and (i['box'][0] > 400 or i['box'][2] > 60):
                portal_type = self.get_text_type(i['raw_text'], prefer_portal, prefix=2)
                if '冒' in i['raw_text'] or '险' in i['raw_text']:
                    portal['nums'] += 1
                elif portal_type is not None:
                    i.update({'score':prefer_portal[portal_type]+10*(portal_type==type), 'type':portal_type, 'nums':portal['nums']+1})
                    if i['score'] > portal['score']:
                        portal = i
                    else:
                        portal['nums'] = i['nums']