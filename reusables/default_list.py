#!/usr/bin/env python
# -*- coding: utf-8 -*-


class defaultlist(list):
    def __init__(self, *args, factory=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.factory = factory

    def __getitem__(self, index):
        if index >= len(self):
            diff = index - len(self) + 1
            for i in range(diff):
                self.append(self.factory())
        return super().__getitem__(index)
