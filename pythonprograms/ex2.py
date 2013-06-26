#!/usr/bin/python
from screenlets.options import StringOption, IntOption, ListOption
import xml.dom.minidom
import webbrowser
import screenlets
import urllib2
import gobject
import pango
import cairo

class RSSSearchScreenlet(screenlets.Screenlet):
    __name__ = 'RSSSearch'
    __version__ = '0.1'
    __author__ = 'John Doe'
    __desc__ = 'An RSS search screenlet.'
    
    topic = 'Windows Phone 7'
    feeds = ['http://www.engadget.com/rss.xml',
             'http://feeds.gawker.com/gizmodo/full']
    interval = 10
    
    __items = []
    __mousesel = 0
    __selected = None
    
    def __init__(self, **kwargs):
        # Customize the width and height.
        screenlets.Screenlet.__init__(self, width=250, height=300, **kwargs)
        self.y = 25
        
    def on_init(self):
        # Add options.
        self.add_options_group('Search Options',
                               'RSS feeds to search and topic to search for.')
        self.add_option(StringOption('Search Options',
            'topic',
            self.topic,
            'Topic',
            'Topic to search feeds for.'))
        self.add_option(ListOption('Search Options',
                                   'feeds',
                                   self.feeds,
                                   'RSS Feeds',
                                   'A list of feeds to search for a topic.'))
        self.add_option(IntOption('Search Options',
                                  'interval',
                                  self.interval,
                                  'Update Interval',
                                  'How frequently to update (in seconds)'))

        self.update()
        
    def update(self):
        """Search selected feeds and update results."""
        
        self.__items = []

        # Go through each feed.
        for feed_url in self.feeds:
            
            # Load the raw feed and find all item elements.
            raw = urllib2.urlopen(feed_url).read()
            dom = xml.dom.minidom.parseString(raw)
            items = dom.getElementsByTagName('item')
            
            for item in items:
                
                # Find the title and make sure it matches the topic.
                title = item.getElementsByTagName('title')[0].firstChild.data
                if self.topic.lower() not in title.lower(): continue
                
                # Shorten the title to 30 characters.
                if len(title) > 30: title = title[:27]+'...'
                
                # Find the link and save the item.
                link = item.getElementsByTagName('link')[0].firstChild.data
                self.__items.append((title, link))

        self.redraw_canvas()

        # Set to update again after self.interval.
        self.__timeout = gobject.timeout_add(self.interval * 1000, self.update)
        
    def on_draw(self, ctx):
        """Called every time the screenlet is drawn to the screen."""
        
        # Draw the background (a gradient).
        gradient = cairo.LinearGradient(0, self.height * 2, 0, 0)
        gradient.add_color_stop_rgba(1, 1, 1, 1, 1)
        gradient.add_color_stop_rgba(0.7, 1, 1, 1, 0.75)
        ctx.set_source(gradient)
        self.draw_rectangle_advanced (ctx, 0, 0, self.width - 20,
                                      self.height - 20,
                                      rounded_angles=(5, 5, 5, 5),
                                      fill=True, border_size=1,
                                      border_color=(0, 0, 0, 0.25),
                                      shadow_size=10,
                                      shadow_color=(0, 0, 0, 0.25))
        
        # Make sure we have a pango layout initialized and updated.
        if self.p_layout == None :
            self.p_layout = ctx.create_layout()
        else:
            ctx.update_layout(self.p_layout)
            
        # Configure fonts.
        p_fdesc = pango.FontDescription()
        p_fdesc.set_family("Free Sans")
        p_fdesc.set_size(10 * pango.SCALE)
        self.p_layout.set_font_description(p_fdesc)

        # Display our text.
        pos = [20, 20]
        ctx.set_source_rgb(0, 0, 0)
        x = 0
        self.__selected = None
        for item in self.__items:
            ctx.save()
            ctx.translate(*pos)
            
            # Find if the current item is under the mouse.
            if self.__mousesel == x and self.mouse_is_over:
                ctx.set_source_rgb(0, 0, 0.5)
                self.__selected = item[1]
            else:
                ctx.set_source_rgb(0, 0, 0)
            
            self.p_layout.set_markup('%s' % item[0])
            ctx.show_layout(self.p_layout)
            pos[1] += 20
            ctx.restore()
            x += 1

    def on_draw_shape(self, ctx):
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        
    def on_mouse_move(self, event):
        """Called whenever the mouse moves over the screenlet."""
        
        x = event.x / self.scale
        y = event.y / self.scale
        self.__mousesel = int((y -10 )/ (20)) -1
        self.redraw_canvas()
    
    def on_mouse_down(self, event):
        """Called when the mouse is clicked."""
        
        if self.__selected and self.mouse_is_over:
            webbrowser.open_new(self.__selected)


if __name__ == "__main__":
    import screenlets.session
    screenlets.session.create_session(RSSSearchScreenlet)
