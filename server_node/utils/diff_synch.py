from diff_match_patch import diff_match_patch

dmp = diff_match_patch()

class diff_synch:
    def __init__(self, text, server_id=None):
        self.shadow_text = text
        self.backup_text = text
        self.own_version = 0
        self.other_version = 0
        self.backup_version = 0
        self.edit_stack = []
        self.server_id = server_id
    
    def recieve_updates(self, edit_stack, last_version, text):
        if last_version < self.own_version:
            self.shadow_text = self.backup_text

        new_shadow_text = self.shadow_text
        max_version = self.other_version
        for patch_text, patch_version in edit_stack:
            if patch_version >= self.other_version:
                patches = dmp.patch_fromText(patch_text)
                text, _ = dmp.patch_apply(patches, text)
                new_shadow_text, _ = dmp.patch_apply(patches, new_shadow_text)
                if patch_version > max_version: max_version = patch_version
        self.other_version = max_version + 1
        self.edit_stack = []

        self.shadow_text = new_shadow_text
        self.backup_text = self.shadow_text

        return text
    
    def send_updates(self, text):
        patches = dmp.patch_make(self.shadow_text, text)
        diff = dmp.patch_toText(patches)
        self.edit_stack.append([diff, self.own_version])
        self.shadow_text = text
        self.own_version += 1
        return self.edit_stack, self.other_version

def test_diff_synch():
    s = diff_synch("")
    s.text = ""
    c = diff_synch("")

    c.text = "abc"
    # client to server
    s.text = s.recieve_updates(*c.send_updates(c.text), s.text)
    c.text = c.recieve_updates(*s.send_updates(s.text), c.text)

    c.text = "abcx"
    s.text = s.recieve_updates(*c.send_updates(c.text), s.text)
    s.text = s.recieve_updates(*c.send_updates(c.text), s.text)
    s.text = s.recieve_updates(*c.send_updates(c.text), s.text)
    s.send_updates(s.text)
    s.send_updates(s.text)
    s.send_updates(s.text)
    #c.recieve_updates(*s.send_updates())

    print("----------------")
    print(c.text, c.shadow_text)
    print(s.text, s.shadow_text)

    print("----------------")
    s.text = "babcx"
    c.text = "grabcx"
    #s.text = s.recieve_updates(*c.send_updates(c.text), s.text)

    updates = s.send_updates(s.text)
    c.text = c.recieve_updates(*updates, c.text)
    updates = s.send_updates(s.text)
    c.text = c.recieve_updates(*updates, c.text)
    c.text = c.recieve_updates(*updates, c.text)
    c.text = c.recieve_updates(*updates, c.text)
    s.text = s.recieve_updates(*c.send_updates(c.text), s.text)

    print("----------------")
    print(c.text, c.shadow_text)
    print(s.text, s.shadow_text)
    print("----------------")
if __name__=="__main__":
    test_diff_synch()