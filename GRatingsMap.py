import folium
import webbrowser

class GRatingsMap:
    def __init__(self):
        self.map = folium.Map(location=[39.080960, -108.556699], zoom_start=12, tiles='Stamen Terrain')
        self.group1 = folium.FeatureGroup(name='Good Reputation')
        self.group2 = folium.FeatureGroup(name='Questionable Reputation')
        self.group3 = folium.FeatureGroup(name='Poor Reputation')

    def fix_text(self, text):
        text = text.split(' ')
        temp = []
        for word in text:
            if len(word) < 3:
                temp.append(word.upper())
            else:
                temp.append(word.capitalize())
        return ' '.join(temp)

    def add_marker(self, name, texts, ratings, links, lat_long_list):
        if texts[0] == '' or lat_long_list[0] == '': return
        name = self.fix_text(name)
        html="""
        <font size='2' face="verdana">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <b>Name:</b><br>
        {0}<br><br>
        <b>Ratings:</b>
        """.format(name)
        for ind, x in enumerate(ratings):
            html = html+'<br><a href={0} target="_blank" style="color: #0078A8 !important; text-decoration:none">'.format(links[ind])+'{0} </a>'.format(links[ind].split('.')[1:2][0].capitalize())
            rtg = int(x[0])
            for _ in range(rtg):
                html = html+'<span class="fa fa-star checked" style="color:orange"></span>'
            if ('.5' in x): 
                html = html+'<span class="fa fa-star-half-o" style="color:orange"></span>'
            rem = 5 if ('.5' not in x) else 4
            for _ in range(rem-rtg):
                html = html+'<span class="fa fa-star" style="color:lightgray"></span>'
        
        if len([x for x in ratings if int(x[0]) < 3]) > 1:
            marker_color = 'red'
        elif len([x for x in ratings if int(x[0]) < 3]) == 1:
            marker_color = 'orange'
        else: 
            marker_color = 'green'
        icon_choice = 'ok' if marker_color == 'green' else 'info-sign'
        iframe = folium.IFrame(html=html, width=225, height=100)
        popup = folium.Popup(iframe, max_width=2650)
        marker = folium.Marker(lat_long_list,
        popup=popup,
        icon=folium.Icon(color=marker_color, icon=icon_choice)
        )
        if marker_color is 'red':
            self.group3.add_child(marker)
        elif marker_color is 'orange':
            self.group2.add_child(marker)
        else:
            self.group1.add_child(marker)

    def save_open(self):
        self.map.add_child(self.group1), self.map.add_child(self.group2), self.map.add_child(self.group3), self.map.add_child(folium.map.LayerControl())
        #folium.Circle(radius=160934, location=[39.080960, -108.556699], color='#3186cc', fill=True, fill_color='#3186cc').add_to(self.map)
        self.map.save('GRatingsMap.html')
