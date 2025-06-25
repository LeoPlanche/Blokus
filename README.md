## Blokus

Some code to play a 1v1 version of the Blokus game, the pieces are the same as in the original game, the board is 12x12.
I coded this not to be able to play the game, but to be able to code an IA that plays the game. It is still playable and you can face one of the three IAs, or play against someone on the same computer, or watch IAs face eachother.
All three IAs are extremly naive. 

`random` plays random moves.

`glouton` plays the largest pieces first and tries to go on the side of the opponent.

`max_angles` plays the largest pieces first and tries to maximise its number of playable squares, while minimizing the number of playable squares for the opponent. A playable square is a square at a diagonal of a piece, while not being adjacent to one.

You are free to code an IA and beat those.
