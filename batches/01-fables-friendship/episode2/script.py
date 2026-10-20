"""Tumble & Pip: Fables About Friendship, long-form episode v2 (about 30 min, 16:9). The Story Stump script.

Each fable becomes a chapter: a short READ scene (Tumble on the stump with the storybook, Pip beside him, they set up
the story and ask the audience something), the fable itself (its 16:9 render), then a TALK scene (Tumble on the
grass, Pip on the stump edge, the book open behind them): what happened, the moral as a call-and-response, a
copy-me activity with real pauses, and a picture quiz on the storybook page. The light runs from golden afternoon
to starry night across the episode.

Beat types (tuples):
  ("T"|"P"|"B", text, tags, tumble_gesture, pip_gesture, look)   a line; B = both together
       look: "cam" (to the audience), "other" (to each other, default), "book"
  ("pause", seconds, tumble_gesture, pip_gesture)                 a real wait for the child to answer or copy
  ("act", name, seconds)                                          action with no words: open_book, turn_page, close_book,
                                                                  pip_arrive, pip_to_paw, pip_to_stump, dance
  ("page", fable, still_seconds, seconds_or_None)                 cut to that fable's picture on the book page (quiz);
                                                                  the following lines play over it until ("endpage",)
Gestures: Tumble: rest wave excited think point_cam point_pip shrug big tiny hug laugh nod shake clap stretch peck
          pull blow flex yawn count silly stomp run slow tiptoe
          Pip: rest hop cheer wave point droop tilt spin peck flutter clap sleepy
UK English throughout. Lines are short (ages 3 to 5); every question gets a pause of 2 s or more."""

FABLE_TITLES = {1: "Tiny Pip, Big Help!", 2: "Sour Apples?", 3: "Pebble, Pebble, Plop!", 4: "Slow and Steady Bo",
                5: "The Other Fox", 6: "Busy Little Ants", 7: "Scarf Off!", 8: "Pip Who Cried Help", 9: "Stronger Together",
                10: "One Good Turn"}
MORALS = {1: "Tiny friends can be big helpers!", 2: "Don't say sour, ask a friend!", 3: "Think it through, try something new!",
          4: "Slow and steady gets there too!", 5: "Love what you've got, and share it!", 6: "Help a little every day!",
          7: "Gentle and kind works best!", 8: "Tell the truth, so friends know!", 9: "Together we're strong!",
          10: "Help a friend, and a friend helps you!"}

def L(who, text, tags="", tg=None, pg=None, look="other"): return (who, text, tags, tg, pg, look)
def pause(s, tg=None, pg=None): return ("pause", s, tg, pg)
def act(name, s): return ("act", name, s)
def page(n, at, s=None): return ("page", n, at, s)
END = ("endpage",)

SCENES = {}
# ------------------------------------------------------------------ intro (golden afternoon)
SCENES["intro"] = dict(mode="read", closed_book=True, beats=[
    act("pip_arrive", 2.6),
    L("P", "Tumble! Tumble! Is it story time?", "[excited]", pg="hop"),
    L("T", "It's story time, Pip!", "[cheerful]", tg="excited", look="other"),
    L("T", "Hello, friends! I'm Tumble.", "[warm] [cheerful]", tg="wave", look="cam"),
    L("P", "And I'm Pip! Hello, hello!", "[giggles]", pg="wave", look="cam"),
    L("T", "Can you wave hello to Pip?", "[warm]", tg="wave", look="cam"),
    pause(2.4, "wave", "wave"),
    L("P", "Hello! I saw you waving!", "[delighted]", pg="cheer", look="cam"),
    L("T", "Welcome to the Story Stump. Our book has ten stories, all about friends.", "[warm]", tg="tiny", look="cam"),
    L("P", "Ten! That's lots and lots!", "[excited]", pg="hop", look="other"),
    L("T", "Let's count to ten on our fingers. Ready?", "[playful]", tg="count", look="cam"),
    L("B", "One, two, three, four, five, six, seven, eight, nine, ten!", "[cheerful] [slowly]", tg="count", pg="hop", look="cam"),
    L("P", "Great counting! Open the book, Tumble!", "[excited]", pg="flutter", look="other"),
    act("open_book", 1.6),
    L("T", "Story number one. A big kite, and a tiny helper.", "[storyteller voice] [warm]", tg="rest", look="book"),
    L("P", "A tiny helper? That's me!", "[giggles]", pg="point", look="cam"),
    L("T", "Let's see what happened!", "[playful]", look="cam"),
])
# ------------------------------------------------------------------ chapter 1: kite (after)
SCENES["talk01"] = dict(mode="talk", fable=1, beats=[
    L("P", "Peck, peck, peck! I pecked the knot!", "[proud]", pg="peck", look="cam"),
    L("T", "You saved me, Pip! I was all tangled up, like a parcel.", "[laughs]", tg="hug"),
    L("P", "Can you peck like me? Peck, peck, peck!", "[playful]", pg="peck", look="cam"),
    pause(2.6, "peck", "peck"),
    L("T", "Great pecking, friends!", "[cheerful]", tg="clap", look="cam"),
    L("T", "I thought Pip was too tiny to help. But I was wrong!", "[warm]", tg="shake"),
    L("T", "Tiny friends can be...", "[warm] [slowly]", tg="point_cam", look="cam"),
    pause(1.6, None, "tilt"),
    L("P", "BIG helpers!", "[cheerful] [shouting]", pg="cheer", look="cam"),
    page(1, 2.0),
    L("T", "Look at this picture. What colour is the kite?", "[curious]", look="cam"),
    pause(2.6),
    L("P", "Red! A big red kite!", "[excited]"),
    L("T", "And who is tiny? Point to Pip!", "[playful]", look="cam"),
    pause(2.4),
    L("P", "That's me! Hee hee!", "[giggles]"),
    END,
    L("T", "Do you help at home? Maybe you put your shoes away, or help to tidy up?", "[warm]", tg="think", look="cam"),
    pause(2.6, "nod", "tilt"),
    L("P", "I bet you're a super helper!", "[warm]", pg="wave", look="cam"),
])
SCENES["read02"] = dict(mode="read", page_from=1, page_to=2, beats=[
    act("turn_page", 1.3),
    L("T", "Story number two. Sour Apples?", "[storyteller voice]", look="book"),
    L("P", "This is the one where you got a bit grumpy!", "[giggles] [whispers]", pg="tilt"),
    L("T", "Maybe a teeny, tiny bit grumpy.", "[embarrassed] [laughs]", look="other"),
    L("T", "There was one red apple, way, way up high.", "[storyteller voice]", look="cam"),
    L("P", "Can you reach up high? Stretch, stretch, stretch!", "[playful]", pg="flutter", look="cam"),
    pause(2.4, None, "flutter"),
    L("T", "Super stretching! Now, let's see if I can reach it.", "[cheerful]", look="cam"),
])
SCENES["talk02"] = dict(mode="talk", fable=2, beats=[
    L("T", "Mmm! That apple was SO sweet!", "[delighted]", tg="hug"),
    L("P", "But you said it was sour!", "[giggles]", pg="point"),
    L("T", "I was wrong. It wasn't sour at all. I was just cross because I couldn't reach.", "[laughs]", tg="shrug"),
    L("P", "When something is too hard, what can we do?", "[curious]", pg="tilt", look="cam"),
    pause(2.2, "think"),
    L("T", "We can ask a friend!", "[cheerful]", tg="point_pip", look="cam"),
    L("P", "Don't say sour...", "[playful] [slowly]", pg="wave", look="cam"),
    pause(1.4),
    L("T", "...ask a friend!", "[cheerful]", tg="excited", look="cam"),
    page(2, 33.0),
    L("P", "Look! Who is pulling the apple down?", "[curious]", look="cam"),
    pause(2.4),
    L("T", "It's Pip! Tug, tug, tug!", "[cheerful]"),
    L("P", "And how many apples can you see? Count with me!", "[playful]", look="cam"),
    pause(2.6),
    L("T", "Just one. One red apple!", "[warm]"),
    END,
    L("T", "Who can you ask for help? Your mummy, your daddy, your teacher?", "[warm]", tg="think", look="cam"),
    pause(2.4, "nod", "tilt"),
    L("P", "Asking for help is a clever thing to do!", "[warm]", pg="cheer", look="cam"),
])
SCENES["read03"] = dict(mode="read", page_from=2, page_to=3, beats=[
    act("turn_page", 1.3),
    L("P", "Ooh! Story number three is MY story!", "[excited]", pg="hop"),
    L("T", "Pebble, Pebble, Plop!", "[storyteller voice]", look="book"),
    L("T", "It was a hot, hot day. Phew!", "[storyteller voice] [sighs]", look="cam"),
    L("P", "And the water was way down at the bottom of a tall jug.", "[worried]", pg="droop"),
    L("T", "How can a little bird get a drink? Hmm, what do you think?", "[curious]", look="cam"),
    pause(2.4, None, "tilt"),
    L("P", "Let's find out!", "[playful]", pg="hop", look="cam"),
])
SCENES["talk03"] = dict(mode="talk", fable=3, beats=[
    L("P", "Plop, plop, plop! The water came up, and up, and up!", "[proud]", pg="flutter", look="cam"),
    L("T", "You dropped in pebbles! How many pebbles, Pip?", "[curious]", tg="think"),
    L("P", "Let's count them together. Ready?", "[playful]", pg="hop", look="cam"),
    L("P", "One!", "[cheerful]", pg="hop", look="cam"),
    L("T", "Two!", "[cheerful]", tg="count", look="cam"),
    L("P", "Three!", "[cheerful]", pg="hop", look="cam"),
    L("T", "Four!", "[cheerful]", tg="count", look="cam"),
    L("B", "Five!", "[cheerful]", tg="excited", pg="cheer", look="cam"),
    L("T", "Five pebbles! Great counting, friends!", "[delighted]", tg="clap", look="cam"),
    L("T", "My paw got stuck, but Pip had a better idea.", "[laughs]", tg="shrug"),
    L("P", "When something is tricky, think it through...", "[warm]", pg="tilt", look="cam"),
    L("T", "...and try something new!", "[cheerful]", tg="nod", look="cam"),
    page(3, 30.0),
    L("T", "Look at the jug. Is the water high, or low?", "[curious]", look="cam"),
    pause(2.4),
    L("P", "It's coming up high! Plop!", "[excited]"),
    END,
    L("T", "Let's do a big drink. Glug, glug, glug... ahh!", "[playful]", tg="hug", look="cam"),
    pause(2.4, "nod", "hop"),
    L("P", "Mmm! Lovely and cool!", "[giggles]", pg="cheer", look="cam"),
])
SCENES["read04"] = dict(mode="read", page_from=3, page_to=4, beats=[
    act("turn_page", 1.3),
    L("T", "Story number four. A race!", "[excited]", look="book"),
    L("T", "I'm super fast! Zoom, zoom!", "[proud]", look="cam"),
    L("P", "And Bo the turtle is super slow.", "[giggles]", pg="tilt"),
    L("T", "Can you run on the spot, like me? Zoom, zoom, zoom!", "[playful]", look="cam"),
    pause(2.4),
    L("P", "Now let's walk slowly, like Bo. Step... by... step.", "[slowly] [warm]", pg="hop", look="cam"),
    pause(2.4),
    L("T", "Who do you think will win? Fast Tumble, or slow Bo?", "[curious]", look="cam"),
    pause(2.4, None, "tilt"),
])
SCENES["talk04"] = dict(mode="talk", fable=4, beats=[
    L("P", "Bo won! Hooray for Bo!", "[cheerful]", pg="cheer", look="cam"),
    L("T", "I stopped for a tiny rest... and I fell fast asleep!", "[laughs]", tg="yawn"),
    L("P", "You were snoring! Zzz... zzz...", "[giggles]", pg="sleepy"),
    L("T", "But I said, well done, Bo! Being a good friend is better than winning.", "[warm]", tg="clap"),
    L("P", "Can you clap for Bo? Well done, Bo!", "[cheerful]", pg="clap", look="cam"),
    pause(2.6, "clap", "clap"),
    L("T", "Slow and steady gets there...", "[slowly] [warm]", tg="slow", look="cam"),
    pause(1.4),
    L("P", "TOO!", "[shouting] [cheerful]", pg="cheer", look="cam"),
    page(4, 34.0),
    L("P", "Look! Who touched the stump first?", "[curious]", look="cam"),
    pause(2.4),
    L("T", "Bo did! Slow and steady Bo!", "[cheerful]"),
    END,
    L("T", "Let's do a big sleepy yawn, like me. Aaah...", "[yawns] [playful]", tg="yawn", look="cam"),
    pause(2.2, "yawn", "sleepy"),
    L("P", "Wake up! Wake up! It's not bedtime yet!", "[giggles]", pg="flutter", look="cam"),
])
SCENES["read05"] = dict(mode="read", page_from=4, page_to=5, beats=[
    act("turn_page", 1.3),
    L("P", "Story number five! The Other Fox.", "[curious]", pg="point"),
    L("T", "I saw another fox down in the stream. And he copied everything I did!", "[surprised]", look="cam"),
    L("P", "Show them your silly face, Tumble!", "[giggles]", pg="hop"),
    L("T", "Bleh!", "[silly] [playful]", look="cam"),
    L("P", "Can you make a silly face too? Bleh!", "[giggles]", pg="hop", look="cam"),
    pause(2.4),
    L("T", "Super silly! Let's see who that other fox is.", "[laughs]", look="cam"),
])
SCENES["talk05"] = dict(mode="talk", fable=5, beats=[
    L("T", "That other fox was me! It was my reflection in the water.", "[laughs]", tg="point_cam"),
    L("P", "Silly Tumble! And your apple went... splash!", "[giggles]", pg="flutter"),
    L("T", "But you shared your berry with me. Half for you, and half for me.", "[warm]", tg="tiny"),
    L("P", "Sharing makes it taste even better!", "[cheerful]", pg="hop"),
    L("T", "What do you like to share? Your toys? Your snacks? A big hug?", "[warm]", tg="hug", look="cam"),
    pause(2.6, "nod", "tilt"),
    L("P", "Love what you've got...", "[warm] [slowly]", pg="wave", look="cam"),
    L("T", "...and share it!", "[cheerful]", tg="excited", look="cam"),
    page(5, 31.0),
    L("T", "Look at the picture. What is Pip sharing?", "[curious]", look="cam"),
    pause(2.4),
    L("P", "My berry! Half for Tumble!", "[cheerful]"),
    END,
    L("T", "Hey, Pip... I think it's time for a dance break!", "[excited]", tg="excited"),
    L("P", "Dance break! Everybody, stand up!", "[excited] [shouting]", pg="flutter", look="cam"),
])
SCENES["break"] = dict(mode="dance", beats=[
    act("dance", 0.0),                      # the dance song (break song) plays; lines inside it are sung
    L("T", "Phew! Great dancing, everybody!", "[out of breath] [laughs]", tg="excited", look="cam"),
    L("P", "Now sit down, nice and comfy, for more stories.", "[warm]", pg="wave", look="cam"),
    pause(2.0, "nod", "sleepy"),
])
SCENES["read06"] = dict(mode="read", page_from=5, page_to=6, beats=[
    act("turn_page", 1.3),
    L("T", "Story number six. Busy Little Ants.", "[storyteller voice]", look="book"),
    L("P", "The ants worked hard all day, carrying seeds to their home.", "[warm]", pg="hop"),
    L("T", "And I just wanted to play in the crunchy leaves! Crunch, crunch!", "[playful]", look="cam"),
    L("P", "Can you be a busy ant? Carry a seed on your head, and march, march, march!", "[playful]", pg="hop", look="cam"),
    pause(2.8, None, "hop"),
    L("T", "What busy ants!", "[delighted]", look="cam"),
])
SCENES["talk06"] = dict(mode="talk", fable=6, beats=[
    L("T", "Brrr! When the snow came, my tummy rumbled.", "[shivering]", tg="hug"),
    L("P", "And the ants shared their snack with you!", "[warm]", pg="tilt"),
    L("T", "That was so kind. So the next day, I carried the biggest seed of all!", "[proud]", tg="big"),
    L("P", "How do you help at home? Do you tidy your toys? Do you feed your pet?", "[curious]", pg="point", look="cam"),
    pause(2.6, "think", "tilt"),
    L("T", "Help a little...", "[warm] [slowly]", tg="tiny", look="cam"),
    L("P", "...every day!", "[cheerful]", pg="cheer", look="cam"),
    page(6, 31.0),
    L("P", "Look! Who is sharing a snack?", "[curious]", look="cam"),
    pause(2.4),
    L("T", "The ants! Thank you, ants!", "[warm]"),
    END,
    L("P", "Tumble, the ants are in the next story too!", "[excited]", pg="hop"),
    L("T", "Then let's turn the page!", "[cheerful]", tg="excited", look="cam"),
])
SCENES["read07"] = dict(mode="read", page_from=6, page_to=10, beats=[
    act("turn_page", 1.3),
    L("T", "Story number seven. One Good Turn.", "[storyteller voice]", look="book"),
    L("P", "Oh no! It starts with a little ant, spinning in the water!", "[worried]", pg="droop"),
    L("T", "Who can help the little ant? What do you think?", "[curious]", look="cam"),
    pause(2.4, None, "tilt"),
    L("P", "Me! I've got an idea!", "[excited]", pg="cheer", look="cam"),
])
SCENES["talk10"] = dict(mode="talk", fable=10, beats=[
    L("P", "I got stuck in the sticky honey, and the ants pulled me out!", "[giggles]", pg="flutter"),
    L("T", "Let's pull like the ants. Heave, ho! Heave, ho!", "[playful]", tg="pull", look="cam"),
    pause(2.6, "pull", "flutter"),
    L("P", "POP!", "[shouting] [cheerful]", pg="spin", look="cam"),
    L("T", "Pip helped the little ant. And then the ants helped Pip!", "[warm]", tg="point_pip"),
    L("P", "Help a friend...", "[warm] [slowly]", pg="wave", look="cam"),
    L("T", "...and a friend helps you!", "[cheerful]", tg="hug", look="cam"),
    page(10, 8.0),
    L("T", "Look! What is the ant riding on?", "[curious]", look="cam"),
    pause(2.4),
    L("P", "A leaf boat! I dropped it in!", "[proud]"),
    END,
    L("T", "Who has helped you today? Can you say thank you?", "[warm]", tg="think", look="cam"),
    pause(2.4, "nod", "tilt"),
    L("P", "Thank you! Thank you!", "[cheerful]", pg="cheer", look="cam"),
])
SCENES["read08"] = dict(mode="read", page_from=10, page_to=9, beats=[
    act("turn_page", 1.3),
    L("T", "Story number eight. Stronger Together.", "[storyteller voice]", look="book"),
    L("T", "I can snap one little twig. Snap! Easy!", "[proud]", look="cam"),
    L("P", "But can you snap a great big bundle of sticks?", "[curious]", pg="tilt"),
    L("T", "Easy peasy!", "[confident]", look="cam"),
    L("P", "Hmm... I don't think so! What do you think, friends?", "[giggles]", pg="tilt", look="cam"),
    pause(2.2),
])
SCENES["talk09"] = dict(mode="talk", fable=9, beats=[
    L("T", "The bundle went BOING, and I went flying!", "[laughs]", tg="excited"),
    L("P", "One stick is easy to snap. But lots of sticks together are strong!", "[warm]", pg="point"),
    L("T", "Just like friends. Together, we're...", "[warm] [slowly]", tg="point_cam", look="cam"),
    pause(1.4),
    L("P", "STRONG!", "[shouting] [cheerful]", pg="cheer", look="cam"),
    L("T", "Show me your big strong arms! Strong, strong, strong!", "[playful]", tg="flex", look="cam"),
    pause(2.6, "flex", "cheer"),
    page(9, 33.5),
    L("P", "Look! What did we make with the sticks?", "[curious]", look="cam"),
    pause(2.4),
    L("T", "A bridge! A bridge over the stream!", "[delighted]"),
    END,
    L("P", "Who do you like to play with? Your brother, your sister, your friends at nursery?", "[warm]", pg="tilt", look="cam"),
    pause(2.4, "nod", "tilt"),
    L("T", "Playing together is the best!", "[cheerful]", tg="hug", look="cam"),
])
SCENES["read09"] = dict(mode="read", page_from=9, page_to=7, beats=[
    act("turn_page", 1.3),
    L("P", "Story number nine. Scarf Off!", "[cheerful]", pg="hop"),
    L("T", "I had my stripy scarf, all snug and warm.", "[storyteller voice] [warm]", look="cam"),
    L("P", "And the Wind and the Sun had a friendly game. Who can get the scarf off?", "[curious]", pg="tilt"),
    L("T", "Can you blow like the wind? Whoooosh!", "[playful]", look="cam"),
    pause(2.4, None, "flutter"),
    L("P", "Whoa! You nearly blew me away!", "[giggles]", pg="flutter", look="cam"),
])
SCENES["talk07"] = dict(mode="talk", fable=7, beats=[
    L("T", "The wind blew and blew, but I held on tight!", "[laughs]", tg="hug"),
    L("P", "Then the sun shone, soft and warm. And you took your scarf off all by yourself!", "[warm]", pg="tilt"),
    L("T", "Ahh, warm and cosy.", "[content] [sighs]", tg="stretch"),
    L("P", "Gentle and kind...", "[warm] [slowly]", pg="wave", look="cam"),
    L("T", "...works best!", "[warm]", tg="nod", look="cam"),
    L("T", "Can you give yourself a gentle hug? Like this. Squeeze!", "[warm]", tg="hug", look="cam"),
    pause(2.6, "hug", "sleepy"),
    L("P", "Aww. That's a lovely hug.", "[warm]", pg="cheer", look="cam"),
    page(7, 33.0),
    L("T", "Look at the picture. What is the sun doing?", "[curious]", look="cam"),
    pause(2.4),
    L("P", "Smiling! A big sunny smile!", "[cheerful]"),
    END,
    L("T", "Look, Pip. The sun is going down. The sky is getting dark.", "[softly]", tg="point_cam"),
    L("P", "Just one more story, please?", "[sleepy] [softly]", pg="droop", look="other"),
])
SCENES["read10"] = dict(mode="read", page_from=7, page_to=8, beats=[
    act("turn_page", 1.3),
    L("T", "Story number ten. The very last one.", "[softly] [storyteller voice]", look="book"),
    L("P", "This one is about me... being a bit silly.", "[shy]", pg="droop"),
    L("T", "Pip Who Cried Help.", "[storyteller voice]", look="book"),
    L("P", "I pretended I needed help. Just for a joke.", "[shy] [giggles]", pg="tilt"),
    L("T", "Is it a good idea to pretend you need help? Hmm...", "[curious]", look="cam"),
    pause(2.4, None, "droop"),
])
SCENES["talk08"] = dict(mode="talk", fable=8, beats=[
    L("P", "I'm sorry I played tricks on you, Tumble.", "[sorry] [softly]", pg="droop"),
    L("T", "That's okay, Pip. I'm just glad you're safe.", "[warm] [softly]", tg="hug"),
    L("T", "When we tell the truth, our friends know when we really need them.", "[warm]", tg="nod", look="cam"),
    L("P", "Tell the truth...", "[softly]", pg="wave", look="cam"),
    L("T", "...so friends know.", "[softly]", tg="nod", look="cam"),
    L("P", "Saying sorry is brave. Can you say sorry, like me? Sorry!", "[softly]", pg="tilt", look="cam"),
    pause(2.4, "nod", "droop"),
    L("T", "And then we have a big hug. Ahh.", "[warm]", tg="hug", look="cam"),
    page(8, 34.2),
    L("P", "Look. Who lifted the lid and found me?", "[softly] [curious]", look="cam"),
    pause(2.4),
    L("T", "I did! Because friends help friends.", "[warm]"),
    END,
])
SCENES["outro"] = dict(mode="read", page_from=8, page_to="end", night=True, beats=[
    L("T", "That was all ten stories!", "[softly] [yawns]", look="cam"),
    L("P", "Let's sing about everything we learned!", "[sleepy] [softly]", pg="sleepy", look="other"),
    act("recap_song", 0.0),                 # the recap song (one moral line per story, pictures on the pages)
    L("T", "Look at all the stars. It's time to close the book.", "[whispers]", look="cam"),
    act("close_book", 1.8),
    L("P", "Goodnight, Tumble.", "[sleepy] [whispers]", pg="sleepy"),
    L("T", "Goodnight, Pip. Goodnight, friends.", "[whispers] [warm]", tg="wave", look="cam"),
    L("B", "See you next time!", "[whispers] [warm]", tg="wave", pg="wave", look="cam"),
    pause(3.0, None, "sleepy"),
])

ORDER = ["intro", 1, "talk01", "read02", 2, "talk02", "read03", 3, "talk03", "read04", 4, "talk04", "read05", 5, "talk05",
         "break", "read06", 6, "talk06", "read07", 10, "talk10", "read08", 9, "talk09", "read09", 7, "talk07", "read10", 8,
         "talk08", "outro"]
