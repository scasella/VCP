import folium
import webbrowser

class YelpMap:
    def __init__(self):
        self.map = folium.Map(location=[39.080960, -108.556699], zoom_start=10, tiles='Stamen Terrain')
        self.temp_group_1 = []
        self.temp_group_2 = []
        self.temp_group_3 = []

    def add_marker(self, name, rating, reviews, link, lat_long_list):
        if rating == '' or lat_long_list[0] == '': return 
        reviews_html = ''
        if len(reviews) < 1: 
            reviews_html = '<br>None<br><br>' 
        else:
            for date, text in reviews:
                if text == '': continue 
                reviews_html = reviews_html + '<p><b>{0}</b> - {1}</p>'.format(date, text)
        html="""
        <font size='2' face="verdana">
        <b>Name:</b><br>
        {0}<br><br>
        <b>Rating:</b><br>
        <div></div><br><br>
        <b>Negative Reviews:</b>
        {1}
        <a href={2} target="_blank" style="color: #0078A8 !important; text-decoration:none"><b>See Yelp Page</b></a>
        """.format(name, reviews_html, link)
        rating_code = str(-24*(float(rating)/0.5)+24)
        marker_color = 'red' if int(rating[0]) is 1 else 'orange' if int(rating[0]) is 2 else 'green'
        icon_choice = 'info-sign' if int(rating[0]) < 3 else 'ok'
        style_str = '<style>div { background: url(https://s3-media2.fl.yelpcdn.com/assets/srv0/yelp_design_web/9b34e39ccbeb/assets/img/stars/stars.png) no-repeat;background-size: 132px 560px; display: inline-block;vertical-align: middle; width: 132px; height: 24px; background-position: 0 '+rating_code+'px; } </style>'
        iframe = folium.IFrame(html=html, width=300, height=185).add_child(folium.Element(style_str))
        popup = folium.Popup(iframe, max_width=2650)
        marker = folium.Marker(lat_long_list,
        popup=popup,
        icon=folium.Icon(color=marker_color, icon=icon_choice))
        if marker_color is 'red':
            self.temp_group_3.append(marker)
        elif marker_color is 'orange':
            self.temp_group_2.append(marker)
        else:
            self.temp_group_1.append(marker)

    def save_open(self):
        self.group1 = folium.FeatureGroup(name='Good Rating ({0})'.format(len(self.temp_group_1)))
        self.group2 = folium.FeatureGroup(name='Poor Rating ({0})'.format(len(self.temp_group_2)))
        self.group3 = folium.FeatureGroup(name='Bad Rating ({0})'.format(len(self.temp_group_3)))

        [self.group1.add_child(x) for x in self.temp_group_1]
        [self.group2.add_child(x) for x in self.temp_group_2]
        [self.group3.add_child(x) for x in self.temp_group_3]

        self.map.add_child(self.group1), self.map.add_child(self.group2), self.map.add_child(self.group3), self.map.add_child(folium.map.LayerControl())
        #folium.Circle(radius=160934, location=[39.080960, -108.556699], color='#3186cc', fill=True, fill_color='#3186cc').add_to(self.map)
        self.map.save('YelpMap.html')
