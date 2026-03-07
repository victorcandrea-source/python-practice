import uuid

EVENT_LOG = []

def add_event(name:str, pryoriti:str = 'LOW', **kwargs):
    
    event_id = str(uuid.uuid4())
    new_event = {
        'id' : event_id,
        'name' : name,
        'pryoriti' : pryoriti,
    }
    new_event.update(kwargs)
    EVENT_LOG.append(new_event)
    return new_event
