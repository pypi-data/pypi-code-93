from easy_pil import Editor, Text, Font, Canvas, font


profile = Editor("pfp.png").resize((150, 150))
background = Editor("bg.png").resize((900, 300), crop=True)

profile_back = Editor(Canvas((190, 300), "#ffffff42"))
rep_back = Editor(Canvas((150, 50), "#3FA0FF3B")).rounded_corners(radius=5)
prog_back = Editor(Canvas((584, 34), "#A7A9AC91")).rounded_corners(radius=10)
prog_bar = Editor(Canvas((584, 34)))

background.paste(profile_back, (40, 0))
background.paste(profile, (60, 20))

background.paste(rep_back, (60, 220))
background.text((135, 235), "+99", font=Font().montserrat(size=24), color="#ffffff", align="center")
background.text((275, 30), "Shahriyar", font=Font().montserrat(size=50), color="#ffffff")
background.text((275, 85), "#9770", font=Font().montserrat(size=20), color="#BCBEC0")
background.text((875, 42), "#55", font=Font().montserrat(size=45), color="#ffffff", align="right")

background.paste(prog_back, (275, 220))
prog_bar.bar((0, 0), 580, 30, 40, "#A7A9AC91", radius=8)
background.paste(prog_bar, (277, 222))
background.text((570, 226), "23904 / 3443445", font=Font().montserrat(size=20), color="white", align="center")

background.text((275, 265), "Level : 10", font=Font().montserrat(size=18), color="white", align="left")
background.text((863, 265), "Next Role : Bull", font=Font().montserrat(size=18), color="white", align="right")
background.show()
