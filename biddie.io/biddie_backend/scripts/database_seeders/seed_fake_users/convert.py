f = open('girl_photo_counts')
lines = [l.strip('\n') for l in f.readlines()]

current_shit = lines[0]
count = 0
print '{'
for l in lines[1:]:
    if 'girl_photos' in l:
        print '\t%s %s,' % (current_shit, count)
        current_shit = l
        count = 0
    else:
        count += 1
print '}'
