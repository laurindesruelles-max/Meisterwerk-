import sys; sys.argv=["x","none"]
from main import segs, CH, TOTAL
def ts(t): t=int(t); return f"{t//60}:{t%60:02d}"
chap=[("0:00","Intro: Unter dem Brennerpass")]+[(ts(s),CH[int(n[4:])]) for n,s,d in segs if isinstance(n,str) and n.startswith("card")]
desc = """Unter dem Brennerpass entsteht – nach Angaben der Betreiber – die längste unterirdische Eisenbahnverbindung der Welt: der Brenner-Basistunnel. 55 Kilometer von Innsbruck bis Franzensfeste, 64 mit der Umfahrung Innsbruck, rund 230 Kilometer Tunnel insgesamt. Wir zeigen in 3D, wie Tunnelbohrmaschinen wie „Flavia“ sich durch die Alpen fressen, warum es einen dritten Tunnel unter den Röhren gibt, wie der Berg sich wehrt – und warum der Tunnel ausgerechnet in Deutschland einen Haken hat.

KAPITEL
""" + "\n".join(f"{a} {b}" for a,b in chap) + """

💬 Welches Megaprojekt sollen wir als Nächstes auseinandernehmen? Schreib es in die Kommentare!
🔔 Abonniere Meisterwerk und aktiviere die Glocke, damit du kein Video verpasst.

QUELLEN
• Wikipedia: Brennerbasistunnel – https://de.wikipedia.org/wiki/Brennerbasistunnel
• Wikipedia (EN): Brenner Base Tunnel – https://en.wikipedia.org/wiki/Brenner_Base_Tunnel
• ORF (20.10.2026): Brenner-Basistunnel verzögert und verteuert – https://orf.at/stories/3445669/
• SN (28.07.2026): Durchschlag der Haupttunnelröhren – https://www.sn.at/wirtschaft/oesterreich/brennerbasistunnel-durchschlag-der-haupttunnelroehren-art-664543
• Brenner-Nordzulauf (19.09.2025): Historischer Durchschlag im Erkundungsstollen – https://www.brennernordzulauf.eu/newsreader/2025-09-19-historischer-durchschlag-im-brenner-basistunnel.html
• BBT SE: TBM Flavia erreicht den Brenner – https://www.bbt-se.com/en/newsroom/detail/flavia-has-reached-the-brenner-pass-the-last-italian-tbm-of-the-bbt-project-has-completed-its-journey/
• Tiroler Tageszeitung (09.07.2025): Fast 90 Prozent sind gegraben – https://www.tt.com/artikel/30912447/meilenstein-beim-brenner-basistunnel-fast-90-prozent-sind-gegraben
• ADAC (14.01.2025): Brenner-Basistunnel – So weit ist das Rekordbauwerk – https://www.adac.de/news/brenner-basistunnel/
• Vienna.at/VOL (08.01.2026): Lkw-Verkehr am Brenner (Asfinag-Zählung 2025) – https://www.vienna.at/brennerautobahn-lkw-chaos-nimmt-weiter-zu/9908207
• stol.it (28.05.2026): Hotspot Brenner – drei Mal mehr Lkw als in der gesamten Schweiz – https://www.stol.it/artikel/wirtschaft/hotspot-brenner-drei-mal-mehr-lkw-als-in-der-gesamten-schweiz

Alle 3D-Szenen sind vereinfachte, schematische Darstellungen. Stimmungsbilder KI-generiert.

#BrennerBasistunnel #Megaprojekt #Tunnelbau #Meisterwerk"""
open("/home/claude/mw-work/002/out/description.txt","w").write(desc)
print(desc[:900]); print("TOTAL", ts(TOTAL))
