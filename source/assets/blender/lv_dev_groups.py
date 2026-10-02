if grp == 'sofa':
    lv_seat.sofa((0.88, 1.25, F), 90)
elif grp == 'chairs':
    lv_seat.armchair_yellow((-2.55, 1.75, F), -148.4)
    lv_seat.armchair_teal((-2.6, -0.75, F), -176.0 if False else math.degrees(math.atan2(-0.85, 1.0)))
elif grp == 'tea':
    lv_items.tea_set(-1.75, 0.65, F + 0.42, 90)
    lv_items.book_open(V(-1.72, 0.05, F + 0.42), 75)
    lv_items.reading_glasses(V(-1.66, 0.12, F + 0.436), 40)
    lv_items.candlestick((-1.95, 0.32, F + 0.42), h=0.1, lit=True)
    lv_items.oil_lamp((-3.4, 1.85, F + 0.58))
elif grp == 'shelf':
    import lv_tables, lv_books
    r_ = lv_books.bookshelf((-4.09, 2.0, F), -90)
    print('BOOKS', r_[1], 'books')
elif grp == 'table':
    import lv_tables
    lv_tables.coffee_table((-1.75, 0.35, F), 90)
    lv_tables.side_table((-3.4, 1.85))
    lv_tables.newspaper(Matrix.Translation((-1.75, 0.35, F + 0.126)), seed=2)
    lv_tables.knitting_basket((-2.0, -0.55, F))
elif grp == 'sim':
    import lv_wall
    lv_seat.sofa((0.88, 1.25, F), 90)
    lv_wall.curtain_window(1, -2.9, -3.235, 2.8, 1.3, 1.5, 180, '#c9b79a')
elif grp == 'clock':
    import lv_wall
    lv_wall.clock_longcase((-1.0, -3.1, F), 0)
    lv_wall.antlers((1.4, 1.25, 2.62), 90)
elif grp == 'mantel':
    import lv_fire
    lv_fire.mantel_decor()
    lv_fire.bellows((-3.64, 0.93, F), 180)
    lv_fire.log_basket((-3.5, -1.25, F), 0)
    import lv_tables
    lv_tables.knitting_basket((-2.0, -0.62, F))
elif grp == 'frame':
    lv_items.photo_frame(V(-3.78, 0.0, 1.6), -90 + 8, w=0.14, h=0.19, tilt=12, seed=1, fmat='wood_dark', fcol=(0.5, 0.33, 0.22))
