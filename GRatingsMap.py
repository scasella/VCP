import folium
import webbrowser

class GRatingsMap:
    def __init__(self):
        self.map = folium.Map(location=[39.080960, -108.556699], zoom_start=12, tiles='Stamen Terrain')
        self.temp_group_1 = []
        self.temp_group_2 = []
        self.temp_group_3 = []

    def fix_text(self, text):
        text = text.split(' ')
        temp = []
        for word in text:
            if len(word) < 3:
                temp.append(word.upper() if word.lower() != 'of' else word.lower())
            else:
                temp.append(word.capitalize())
        return ' '.join(temp)

    def add_marker(self, name, ratings, links, counts, lat_long_list):
        if lat_long_list[0] == '': return
        name = self.fix_text(name)
        overall_rtg = self._get_overall_rtg(ratings, counts)
        html="""
        <font size='2' face="verdana">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <b>Name:</b><br>
        {0}<br><br>
        <b>Overall Rating:</b><br>
        {1}<br><br>
        <b>Ratings:</b>
        """.format(name, overall_rtg)
        for ind, x in enumerate(ratings):
            html+='<br><a href={0} target="_blank" style="color: #0078A8 !important; text-decoration:none">'.format(links[ind])+'{0} </a>'.format(links[ind].split('.')[1:2][0].capitalize())
            rtg = int(x[0])
            for _ in range(rtg):
                html+='<span class="fa fa-star checked" style="color:orange"></span>'
            rem = 4
            if int(("%.2f" % float(x)).split('.')[1]) >= 50: 
                html+='<span class="fa fa-star checked" style="color:orange"></span>'
            elif int(("%.2f" % float(x)).split('.')[1]) >= 25:
                html+='<span class="fa fa-star-half-o" style="color:orange"></span>'
            else:
                rem = 5
            for _ in range(rem-rtg):
                html+='<span class="fa fa-star" style="color:lightgray"></span>'
            html+='<span style="color:lightgray">&nbsp{0}</span>'.format(counts[ind])
        
        if float(overall_rtg) <= 2.0:
            marker_color = 'red'
        elif (float(overall_rtg) > 2.0) and (float(overall_rtg) < 3.0):
            marker_color = 'orange'
        else: 
            marker_color = 'green'
        icon_choice = 'ok' if marker_color == 'green' else 'info-sign'
        iframe = folium.IFrame(html=html, width=225, height=160)
        popup = folium.Popup(iframe, max_width=2650)
        marker = folium.Marker(lat_long_list,
        popup=popup,
        icon=folium.Icon(color=marker_color, icon=icon_choice)
        )
        if marker_color is 'red':
            self.temp_group_3.append(marker)
        elif marker_color is 'orange':
            self.temp_group_2.append(marker)
        else:
            self.temp_group_1.append(marker)

    def _get_overall_rtg(self, ratings, counts):
        total = sum([int(x) for x in counts])
        #Weighted average rating, truncate at two decimal places
        overall_rtg = str(int(sum([float(rating)*(int(counts[ind])/total) for ind, rating in enumerate(ratings)])*100)/100)
        return overall_rtg if (overall_rtg[-2] != '.') else overall_rtg+'0'

    def save_open(self):
        self.group1 = folium.FeatureGroup(name='Good Reputation ({0})'.format(len(self.temp_group_1)))
        self.group2 = folium.FeatureGroup(name='Questionable Reputation ({0})'.format(len(self.temp_group_2)))
        self.group3 = folium.FeatureGroup(name='Poor Reputation ({0})'.format(len(self.temp_group_3)))

        [self.group1.add_child(x) for x in self.temp_group_1]
        [self.group2.add_child(x) for x in self.temp_group_2]
        [self.group3.add_child(x) for x in self.temp_group_3]

        self.map.add_child(self.group1), self.map.add_child(self.group2), self.map.add_child(self.group3), self.map.add_child(folium.map.LayerControl())
        #folium.Circle(radius=160934, location=[39.080960, -108.556699], color='#3186cc', fill=True, fill_color='#3186cc').add_to(self.map)
        self.map.save('GRatingsMap.html')
