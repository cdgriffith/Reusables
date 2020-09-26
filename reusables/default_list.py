#!/usr/bin/env python
# -*- coding: utf-8 -*-


class defaultlist(list):
    def __init__(self, *args, factory=lambda: None, **kwargs):
        super().__init__(*args, **kwargs)
        if not callable(factory):
            raise Exception("The factory must be callable")
        self.factory = factory

    def __getitem__(self, index):
        if index >= len(self):
            for i in range(index - len(self) + 1):
                self.append(self.factory())
        return super().__getitem__(index)
