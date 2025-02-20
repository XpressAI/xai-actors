from xai_components.base import InArg, OutArg, InCompArg, Component, BaseComponent, xai_component
import openai
import os
import requests
import shutil
from thespian.actors import ActorSystem, Actor


@xai_component
class CreateActorsystem(Component):
    def execute(self, ctx) -> None:
        ctx['actor_system'] = ActorSystem()
        

@xai_component
class DefineActor(Component):
    on_message: BaseComponent
    
    name: InCompArg[str]
    actor_ref: OutArg[Actor]
    message: OutArg[any]
    sender: OutArg[Actor]
    
    def execute(self, ctx) -> None:
        class XircuitsActor(Actor):
            def receiveMessage(me, message, sender):
                self.message.value = message
                self.sender.value = sender
                
                is_done, next_body = self.on_message.do(ctx)
                
                while next_body:
                    is_done, next_body = next_body.do(ctx)

        system = ctx['actor_system']
        ref = system.createActor(XircuitsActor, self.name.value)
        
        self.actor_ref.value = ref

@xai_component
class TellActor(Component):
    actor_ref: InCompArg[Actor]
    message: InCompArg[any]
    
    def execute(self, ctx) -> None:
        system = ctx['actor_system']
        system.tell(self.actor_ref.value, self.message.value)

@xai_component
class AskActor(Component):
    actor_ref: InCompArg[Actor]
    message: InCompArg[str]
    wait_time: InArg[int]
    response: OutArg[str]
    
    def execute(self, ctx) -> None:
        system = ctx['actor_system']
        self.response.value = system.ask(self.actor_ref.value, self.message.value, self.wait_time.value)
