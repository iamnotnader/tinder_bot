`import femaleFirstNames from "./female-first-names";`
`import maleFirstNames from "./male-first-names";`
`import lastNames from "./last-names";`

nameGenerator = (sex, firstLetter, lastLetter) ->
  # TODO(daddy): Move all this shit to the server-side later. Currently,
  # the names bloat the size of the page to 800kB....
  if sex is 'f'
    firstName = femaleFirstNames[Math.floor(Math.random() * femaleFirstNames.length)]
  else
    firstName = maleFirstNames[Math.floor(Math.random() * maleFirstNames.length)]


  singleLetterNames = []
  twoLetterNames = []
  for name in lastNames
    if name.substring(0, 2).toLowerCase() is firstName.substring(0, 2).toLowerCase()
      twoLetterNames.push(name)
    else if name.substring(0, 1).toLowerCase() is firstName.substring(0, 1).toLowerCase()
      singleLetterNames.push(name)
  if Math.random() < twoLetterNames.length / (1.0 * (twoLetterNames.length + singleLetterNames.length))
    index = Math.floor(Math.random() * twoLetterNames.length)
    return [firstName, twoLetterNames[index]]
  else
    index = Math.floor(Math.random() * singleLetterNames.length)
    return [firstName, singleLetterNames[index]]


`export default nameGenerator`

