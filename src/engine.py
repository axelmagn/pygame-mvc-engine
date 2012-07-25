# System Library Imports
from weakref import WeakKeyDictionary

# 3rd Party Library Imports
import pygame
from pygame.locals import *

# Local Imports

# ==============================================================================
# EVENTS
# ==============================================================================
class Event:
  """
  The superclass for any events, message objects for the middleman between
  engine entities

  """
  def __init__(self):
    self.name = "Generic Event"

class DrawEvent(Event):
  """
  The event for when the CPU Spinner wants the main view to update the display

  """
  def __init__(self):
    self.name = "Draw Event"

class UpdateEvent(Event):
  """
  The event for when the CPU Spinner wants to update the game state

  """
  def __init__(self):
    self.name = "Update Event"

class QuitEvent(Event):
  """
  Quit signal

  """
  def __init__(self):
    self.name = "Quit Event"

class QuitCleanupEvent(Event):
  """
  Do any cleaning up after the game has quit (AFTER Run loop)

  """
  def __init__(self):
    self.name = "Cleanup Event"

# ------------------------------------------------------------------------------
class EventManager:
  """
  Root-level middleman entity that coordinates messages passed between engine
  entities

  """
  def __init__(self):
    self.listeners = WeakKeyDictionary()

  def RegisterListener(self, listener):
    self.listeners[ listener ] = 1;

  def UnregisterListener(self, listener):
    if listener in self.listeners.keys():
      del self.listeners[ listener ]

  def Post(self, event):
    """
    Post a new event, broadcasting to all listeners

    """
    for listener in self.listeners.keys():
      listener.Notify( event )

# ==============================================================================
# MODELS
# ==============================================================================

# ==============================================================================
# VIEWS
# ==============================================================================

class PygameView:
  """
  Pygame View

  Attributes
  ----------
  evManager   : event manager that will post events using the Notify Method
  window      : pygame display object
  background  : colored background pygame surface

  """
  def __init__(self, evManager):
    self.evManager = evManager
    self.evManager.RegisterListener( self )
    
    pygame.init()
    self.window = pygame.display.set_mode( (400, 400) )
    pygame.display.set_caption( 'MVC Prototype' )
    self.background = pygame.Surface( self.window.get_size() )
    self.drawBackground()

  def drawBackground(self):
    self.background.fill( (128,128,255) )
    self.window.blit( self.background, (0,0) )
    pygame.display.flip()

  def Notify(self, event):
    if isinstance( event, DrawEvent ):
      # Draw Background
      self.drawBackground()
    if isinstance( event, QuitCleanupEvent ):
      pygame.quit()

# ==============================================================================
class PygameController:
  """
  Takes Pygame events generated by the keyboard and interface, and generates 
  user input events.

  """
  def __init__(self, evManager):
    self.evManager = evManager
    self.evManager.RegisterListener( self )

  def Notify(self, event):
    if isinstance( event, UpdateEvent ):
      for event in pygame.event.get():
        ev = None
        if event.type == QUIT:
          ev = QuitEvent()
        if ev:
          self.evManager.Post( ev )

# ------------------------------------------------------------------------------
class TickController:
  """
  Controller that generates subsecond scheduled events

  """
  def __init__(self, evManager):
    self.evManager = evManager
    self.evManager.RegisterListener( self )
    self.clock = pygame.time.Clock()
    self.running = True

  def Run(self):
    # Main run loop
    while self.running:
      self.evManager.Post( UpdateEvent() )
      self.evManager.Post( DrawEvent() )
      self.clock.tick(30)
      self.evManager.Post( DrawEvent() )
      self.clock.tick(30)
    # after game has quit, clean up assets
    self.evManager.Post( QuitCleanupEvent() )
  
  def Notify(self, event):
    if isinstance( event, QuitEvent ):
      self.running = False

# ==============================================================================
# MAIN SCRIPT
# ==============================================================================
def main():
  evManager = EventManager()
  
  pygamec = PygameController( evManager )
  spinner = TickController( evManager )
  pygamev = PygameView( evManager )

  spinner.Run()

if __name__ == "__main__":
  main()
