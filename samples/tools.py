# Recolor
# sup = initSupabase()
# gr = getCourses(sup=sup)
# rnd = random.Random()
# for i in gr:
#     color = f'{255},{rnd.randint(0, 255)},{rnd.randint(0, 255)},{rnd.randint(0, 255)}'
#     sup.table('Courses').update({'color': color}).eq('id', i.id).execute()