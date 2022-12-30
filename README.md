<center>
    <img src="https://img.itch.zone/aW1nLzY3MDQyOTcucG5n/original/9RjANB.png" width="200" />
    <h1>…AI bot </h1>
</center>

UP TO DEATH is an adventure hypercasual game created by our friend Rachit
Vasudeva [[itch.io](https://itch.io/profile/rachit-vasudeva)]

From the game's page [[link](https://rachit-vasudeva.itch.io/up-to-death)]:

> "This, is UP TO DEATH, an adventure hypercasual game in which you have to
> rescue CUBEY, from being collided with the horde of spikes at the top. Collect
> as much stars as you can, create a monster score and compete with your
> friends."

Inspired by a video from
_[ClarityCoders](https://www.youtube.com/@ClarityCoders)_ on using an Image
Classifier model to create a bot to play Fall Guys, we decided to give that
technique a try and apply it on _UP TO DEATH_.

The base of the source code is a fork of ClarityCoder's repo. We have made many
changes in the scripts to suit our needs in detecting the game screen anywhere
on the display, creating scripts to create training data while the human (us) is
playing and another script to process bad runs, associate keystrokes with
screenshots

## Demo

The technique is mainly to associate a keystroke to a screen capture in the game
and hope the model picks up the pattern, which is visible in the demo run
trained on a dataset of 97 thousand images. We were able to a recorded high
score of 14 after many tries

We were also observed that the model exhibited our gameplay styles and sometimes
that showed up uniquely such as Ya-s-h's "wiggling left and right" tactic

<!-- TODO: INSERT VIDEO -->

you can find the colab file used to train the model on their video:
[FastAI learns to play Fall Guys](https://youtu.be/GS_0ZKzrvk0)

## Credits

- Rachit, for creating the game
- ClarityCoders for sparking the idea
