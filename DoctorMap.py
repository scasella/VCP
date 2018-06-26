import folium
import webbrowser

class DoctorMap:
    def __init__(self):
        self.map = folium.Map(location=[39.080960, -108.556699], zoom_start=12, tiles='Stamen Terrain')
        self.group1 = folium.FeatureGroup(name='Active License')
        self.group2 = folium.FeatureGroup(name='Conditional License')
        self.group3 = folium.FeatureGroup(name='Expired License')

    def fix_text(self, text):
        text = text.split(' ')
        temp = []
        for word in text:
            if len(word) < 3:
                temp.append(word.upper())
            else:
                temp.append(word.capitalize())
        return ' '.join(temp)

    def add_marker(self, name, status, org, link, multiple, lat_long_list):
        if lat_long_list[0] == '' or status == 'None': return 
        name, org = self.fix_text(name), self.fix_text(org)
        html="""
        <font size='2' face="verdana">
        <b>Name:</b><br>
        {0}<br><br>
        <b>Organization:</b><br>
        {1}<br><br>
        <b>License Status:</b><br>
        {2}<br><br>
        <a href={3} target="_blank" style="color: #0078A8 !important; text-decoration:none"><b>View License</b></a>
        """.format(name, org, status, link)
        if status == 'Active - With Conditions':
            marker_color = 'orange'
        elif status == 'Expired':
            marker_color = 'red'
        else: 
            marker_color = 'green'
        icon_choice = 'ok' if marker_color == 'green' else 'info-sign'
        iframe = folium.IFrame(html=html, width=225, height=180)
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
        self.map.save('DoctorMap.html')
