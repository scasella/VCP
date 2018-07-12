import folium
import webbrowser

class HealthgradesMap:
    def __init__(self):
        self.map = folium.Map(location=[39.080960, -108.556699], zoom_start=12, tiles='Stamen Terrain')
        self.temp_group_1 = []
        self.temp_group_2 = []
        self.temp_group_3 = []
        
        

    def add_marker(self, name, rating, link, malpractice, sanctions, board, address):
        if rating == 0.0 or address[0] == '': return
        #name = self.fix_text(name)
        #overall_rtg = self._get_overall_rtg(ratings, counts)
        html="""
        <font size='2' face="verdana">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <b>Name:</b><br>
        {0}<br><br>
        <b>Rating:</b><br>
        """.format(name)
        for _ in range(int(rating)):
            html+='<span class="fa fa-star checked" style="color:orange"></span>'
        if ('.5' in str(rating)): 
            html+='<span class="fa fa-star-half-o" style="color:orange"></span>'
        rem = 5 if ('.5' not in str(rating)) else 4
        for _ in range(rem-int(rating)):
            html+='<span class="fa fa-star" style="color:lightgray"></span>'
        #html+='<span style="color:lightgray">&nbsp{0}</span>'.format(counts[ind])
        html+='<br><br><b>Background Check:</b> {0}'.format(self._do_background(malpractice, sanctions, board))
        html+='<br><a href={0} target="_blank" style="color: #0078A8 !important; text-decoration:none">Healthgrades Link</a>'.format(link)

        if float(rating) <= 2.0 or sum([malpractice, sanctions, board]) > 1:
            marker_color = 'red'
        elif ((float(rating) > 2.0) and (float(rating) < 3.0)) or sum([malpractice, sanctions, board]) == 1:
            marker_color = 'orange'
        else: 
            marker_color = 'green'
        icon_choice = 'ok' if marker_color == 'green' else 'info-sign'
        iframe = folium.IFrame(html=html, width=225, height=175)
        popup = folium.Popup(iframe, max_width=2650)
        marker = folium.Marker(address,
        popup=popup,
        icon=folium.Icon(color=marker_color, icon=icon_choice)
        )
        if marker_color is 'red':
            self.temp_group_3.append(marker)
        elif marker_color is 'orange':
            self.temp_group_2.append(marker)
        else:
            self.temp_group_1.append(marker)

    def _do_background(self, mal, sanc, board):
        if all(x == False for x in [mal, sanc, board]):
            return '<li>Clean</li>'
        else:
            reports = ''
            if mal is True:
                reports+='<li>Malpractice</li>'
            if sanc is True:
                 reports+='<li>Sanctions</li>' 
            if board is True:
                reports+='<li>Board Actions</li>'
            return reports 

    def save_open(self):
        self.group1 = folium.FeatureGroup(name='Good Reputation ({0})'.format(len(self.temp_group_1)))
        self.group2 = folium.FeatureGroup(name='Questionable Reputation ({0})'.format(len(self.temp_group_2)))
        self.group3 = folium.FeatureGroup(name='Poor Reputation ({0})'.format(len(self.temp_group_3)))

        [self.group1.add_child(x) for x in self.temp_group_1]
        [self.group2.add_child(x) for x in self.temp_group_2]
        [self.group3.add_child(x) for x in self.temp_group_3]

        self.map.add_child(self.group1), self.map.add_child(self.group2), self.map.add_child(self.group3), self.map.add_child(folium.map.LayerControl())
        #folium.Circle(radius=160934, location=[39.080960, -108.556699], color='#3186cc', fill=True, fill_color='#3186cc').add_to(self.map)
        self.map.save('HealthgradesMap.html')
