# Genetic-Pong

A Neural Network based agent that plays pong and also learns on itself with the help of Genetic Algorithm.    
The Neural Net has been used to predict one move from the two possible moves here- "up" and "down", at a given time.    
Given:   
-  The ratio of the y velocity to x velocity of the ball at a frame.     
-  The difference between vertical position of the ball and the vertical position of the paddle, scaled by the max vertical height.    
-  The absolute vertical position of the paddle.     
These three features form the input of the neural network.    

# Requirements :    
1. Kivy    
2. numpy    

## Running on your local machine:   
- Clone the repository: <code> $ git clone https://github.com/yugrocks/Genetic-Pong.git </code>    
- Go to the base directory:  <code> $cd Genetic-Pong </code>   
- Install requirements: <code> $ pip install -r requirements.txt </code>    
- Run: <code> python training_player2.py </code>    

## Training your own model:   
- The model is defined in the file <code> mover.py </code>. You can modify the neural net articture there, along with the other details in <code> training_player2.py </coed>    
- In order to start training, edit the <code> training_phase </code> variable to <code> True</code>, in the file <code> training_player2.py</code>.    

# About the Genetic Algorithm    
- I have defined two types of crossovers and a mutation criteria.   
- Total Population Size : 20    
- Fitness Function: The number of times the ball hits the paddle in a given game. (Not the best criteria, but will do)      
- The Best two always make it to the next generation.    
- The worst 14 are thrown out.    

## Mutation:    
Probability of mutation: 0.2 </br>   
In mutation, eash element of the bit string is modified by a little random value, depending on the probability of mutation itself.         
That is, the probability of an element of the bit string being modified is 0.2.   

## Crossover 1:   
Probability of Crossover: 0.7</br>  
Crossover is inspired by the idea that two parents create one or more children, each of which may or may not be better than the parents. The best ones further make it to the next generation. In this function, two parents from the best 6 are selected at random, and their elements are swapped accross a given random index. This creates two offsprings.    

## Crossover 2:    
Probability of Crossover2: 0.3 </br>      
This is another kind of crossover in which the elements of the two parents at each index are swapped with a probability of 0.3. This also creates two offsprings.     

# Training Stats:    
Coming Soon.
