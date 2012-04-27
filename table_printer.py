## -*- coding: utf-8 -*-
##
## table_print.py
##
## Author:   Toke Høiland-Jørgensen (toke@toke.dk)
## Date:     26 April 2012
## Copyright (c) 2012, Toke Høiland-Jørgensen
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

def longest_value(values):
    return max(map(len, map(unicode, values)))

def aligned(value, length, align='left'):
    if align == 'left':
        format = "%-"+str(length)+"s"
    else:
        format = "%"+str(length)+"s"
    return format % value

def print_table(dicts, header=None):
    if not header:
        header_items = [""]*(len(dicts)+1)
    else:
        header_items = header
    all_keys = set()
    longest_values = []
    for h,d in zip(header_items[1:], dicts):
        all_keys.update(d.keys())
        longest_values.append(longest_value(d.values()+[h]))

    all_keys = sorted(all_keys)
    longest_key = longest_value(all_keys+[header_items[0]])

    rows = []
    for key in all_keys:
        row = "| "+aligned(key, longest_key)+" "
        for length,d in zip(longest_values,dicts):
            if key in d:
                val = d[key]
            else:
                val = ""
            row += "| "+aligned(val,length, 'right')+" "
        row += "|"
        rows.append(row)

    spacer = re.sub(r"[^\+]", "-", rows[0].replace("|","+"))
    print spacer
    if header:
        row = ""
        for i,h,l in zip(range(len(header)), header, [longest_key]+longest_values):
            if i:
                align = 'right'
            else:
                align = 'left'
            row += "| "+aligned(h,l,align)+" "
        row +="|"
        print row
        print spacer

    for row in rows:
        print row
    print spacer

if __name__ == "__main__":
    d1 = dict(x=2,y=345)
    d2 = dict(y=5, z=6)
    print_table ([d1,d2], ["one", "two", "three"])
