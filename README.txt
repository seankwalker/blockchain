#
# README.txt
#
# Name:  Sean Walker
# NetID: skw34
#
# CPSC 310, Spring 2019
# Homework 4
#
# Driver script for blockchain simulation and answers to questions in Homework
# 4 specification.

# Note: this file can be executed as a shell script via
# ./README.txt

# ~~~ Question 3 ~~~
# start the python script
python3 main.py > /dev/null 2>&1 &
# or comment the above line and uncomment the line below to see server output:
# python3 main.py &
proc_pid=$!

# run through steps (a) thru (e) from spec, sleeping (more than) enough time
# to ensure completion of each one
sleep 2
curl --head localhost:6666/genesis &> /dev/null; sleep 1
curl --head localhost:7777/generate &> /dev/null; sleep 1
curl --head localhost:8888/generate &> /dev/null; sleep 1
curl --head localhost:7777/generate &> /dev/null; sleep 1
curl --head localhost:9999/pull &> /dev/null; sleep 1

# print out state of each node's chain
echo "generator node:"; curl localhost:6666/query; sleep 1; echo "\n"
echo "honest node:"; curl localhost:7777/query; sleep 1; echo "\n"
echo "dishonest node:"; curl localhost:8888/query; sleep 1; echo "\n"
echo "joiner node:"; curl localhost:9999/query; sleep 1; echo "\n"

kill $proc_pid

# ~~~ Question 4 ~~~
# a) The divergence of two chains from some point is called a "fork."
# b) Forks can come about for different reasons. In our case, it occurred
#    because the dishonest node is, well, "dishonest" (and ignores the proper
#    rules of the blockchain). However, forks can occur for other (good)
#    reasons, such as a deliberate rule update which, for instance, increases
#    the security of the protocol. In such a case, one would want to use that
#    forked chain, since it's more secure than the source chain. Examples of
#    such forks would be Bitcoin Cash, which is a fork of the original
#    Bitcoin blockchain. when the original started to struggle due to its
#    limited 1MB block size, the fork was created with a larger block size to
#    improve scalability.