import copy

genesis = {
    "AMM":{"A1":100,"A2":100,"s":100,"fee":0.00},
    "Trader":{"A1":100,"A2":100,"s":0},
    "LP":{"A1":0,"A2":0,"s":100}
    }

def swapToAsset2(state,inputs):
    agent = inputs[0]
    dA1 = inputs[1]
    feeFactor = (1-state["AMM"]["fee"])
    dA2 = state["AMM"]["A2"]/(state["AMM"]["A1"]+dA1*feeFactor)*dA1*feeFactor
    if dA1>0 and state[agent]["A1"]-dA1 >= 0 :
        state["AMM"]["A1"]+=dA1
        state[agent]["A1"]-=dA1
        state["AMM"]["A2"]-=dA2
        state[agent]["A2"]+=dA2

def swapToAsset1(state, inputs):
    agent = inputs[0]
    dA2 = inputs[1]
    feeFactor = (1-state["AMM"]["fee"])
    dA1 = state["AMM"]["A1"]/(state["AMM"]["A2"]+dA2*feeFactor)*dA2*feeFactor
    if dA2>0 and state[agent]["A2"]-dA2 >= 0:
        state["AMM"]["A2"]+=dA2
        state[agent]["A2"]-=dA2
        state["AMM"]["A1"]-=dA1
        state[agent]["A1"]+=dA1

def addLiquidity(state,inputs):
    agent = inputs[0]
    A1=state["AMM"]["A1"]
    A2=state["AMM"]["A2"]
    S= state["AMM"]["s"]
    dA1=min(inputs[1],A1/A2*inputs[2])
    dA2=min(inputs[2],A2/A1*inputs[1])
    if (dA1 <= state[agent]["A1"] and dA2 <= state[agent]["A2"]) and (dA1 > 0 and dA2 > 0):
            state[agent]["A1"]-=dA1
            state[agent]["A2"]-=dA2
            state["AMM"]["A1"]+=dA1
            state["AMM"]["A2"]+=dA2
            dS = min(dA1/A1, dA2/A2) * S
            state["AMM"]["s"] += dS
            state[agent]["s"]+=dS

def removeLiquidity(state,inputs):
    dS = inputs[1]
    agent = inputs[0]
    if dS > 0 and state[agent]["s"]-dS>=0 and state["AMM"]["s"]-dS>=0:
        DA = (1-dS/state["AMM"]["s"])
        A1=state["AMM"]["A1"]
        A2=state["AMM"]["A2"]
        state[agent]["s"]-=dS
        state["AMM"]["A1"]=A1*DA
        state["AMM"]["A2"]=A2*DA
        state[agent]["A1"]+=A1-state["AMM"]["A1"]
        state[agent]["A2"]+=A2-state["AMM"]["A2"]
        state["AMM"]["s"]-=dS


actionList = [
        [ removeLiquidity , [  "LP" , 5 ]],
        [ removeLiquidity , [  "LP" , 5 ]],
        [ removeLiquidity , [  "LP" , 5 ]] ]


def evolve(state, actionStack):
    history = [copy.deepcopy(state)]
    for action in actionStack:
        action[0](state,action[1])
        history.append(copy.deepcopy(state))
    return history 

def check_genesis_block(state):
    no_valid_element = []
    
    for key, agents in state.items():
        for subkey, value in agents.items():
            if not isinstance(value, (int, float)) or value < 0:
                no_valid_element.append((key, subkey, value))
                
    if  no_valid_element:
        print("No valid elements:", no_valid_element)
        return False
    return True

def update_pool_fees(fee):
    if fee <= 1:
        state["LP"]["AMM"]=fee
