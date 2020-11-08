# Copyright 2020 brombinmirko <send@mirko.pm>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gdk, Gio, GdkPixbuf
from urllib.request import urlopen, Request
import requests, json

class API():
    base = "https://api.coingecko.com/api/v3/coins"
    markets = base + "/markets"

class BitmycoinsWindow(Gtk.Window):
    app_name = "Bit my Coins"

    header_bar = Gtk.HeaderBar()
    scroll_view = Gtk.ScrolledWindow()
    btn_sync = Gtk.Button.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
    currencies_liststore = Gtk.ListStore(str, str, float, float, float)
    currencies_filter = currencies_liststore.filter_new()
    currencies_treeview = Gtk.TreeView.new_with_model(currencies_filter)

    def __init__(self):
        Gtk.Window.__init__(self, title = self.app_name)

        self.header_bar.set_show_close_button(True)
        self.header_bar.props.title = self.app_name
        self.header_bar.pack_start(self.btn_sync)
        self.set_titlebar(self.header_bar)

        currencies = requests.get(API.markets + "?vs_currency=eur&order=market_cap_desc&per_page=100&page=1&sparkline=false")
        currencies = json.loads(currencies.text)
        currencies_datalist = []

        currencies_sort = Gtk.TreeModelSort(model=self.currencies_liststore)
        currencies_sort.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        self.currencies_treeview = Gtk.TreeView.new_with_model(self.currencies_filter)

        for currency in currencies:
            currencies_datalist.append((
                # currency['image'],
                currency['symbol'],
                currency['name'],
                currency['price_change_percentage_24h'],
                currency['current_price'],
                currency['high_24h'],
            ))

        for currency in currencies_datalist:
            self.currencies_liststore.append(list(currency))

        for i, column_title in enumerate(["#", "Name", "Change", "Current price", "Max 24h"]):
            '''
            if column_title == "#":
                renderer = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                column.set_cell_data_func(renderer, self.set_tree_cell_pixbuf)
            else:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            '''

            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)

            if i == 2:
                column.set_cell_data_func(renderer, self.set_tree_cell_background)

            column.set_reorderable(True)
            column.set_sort_column_id(i)
            self.currencies_treeview.append_column(column)

        self.scroll_view.add(self.currencies_treeview)
        self.add(self.scroll_view)

    def set_tree_cell_background(self, col, cell, model, iter, user_data):
        if model.get_value(iter, 2) < 0:
            cell.set_property("foreground", "red")
        else:
            cell.set_property("foreground", "green")

    # TODO: thid method should be async
    def set_tree_cell_pixbuf(self, col, cell, model, iter, user_data):
        stream = Gio.MemoryInputStream.new_from_data(
            urlopen(
                Request(
                    model.get_value(iter, 0),
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
            ).read(),
        )
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(stream, 24, 24, True)
        cell.set_property('pixbuf', pixbuf)

win = BitmycoinsWindow()
win.set_default_size(520, 700)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
