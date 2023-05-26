import sys
from time import sleep

import pygame

from bullet import Bullet
from pirate import Pirate


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """Respond to keypresses."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event, ship):
    """Respond to key releases."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_settings, screen, stats, sb, play_button, ship, pirates,
                 bullets):
    """Respond to keypresses and mouse events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button,
                              ship, pirates, bullets, mouse_x, mouse_y)


def check_play_button(ai_settings, screen, stats, sb, play_button, ship,
                      pirates, bullets, mouse_x, mouse_y):
    """Start a new game when the player clicks Play."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # Reset the game settings.
        ai_settings.initialize_dynamic_settings()

        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)

        # Reset the game statistics.
        stats.reset_stats()
        stats.game_active = True

        # Reset the scoreboard images.
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        # Empty the list of pirates and bullets.
        pirates.empty()
        bullets.empty()

        # Create a new fleet and center the ship.
        create_fleet(ai_settings, screen, ship, pirates)
        ship.center_ship()


def fire_bullet(ai_settings, screen, ship, bullets):
    """Fire a bullet, if limit not reached yet."""
    # Create a new bullet, add to bullets group.
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def update_screen(ai_settings, screen, stats, sb, ship, pirates, bullets,
                  play_button):
    """Update images on the screen, and flip to the new screen."""
    # Redraw the screen, each pass through the loop.
    screen.fill(ai_settings.bg_color)

    # Redraw all bullets, behind ship and pirates.
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    pirates.draw(screen)

    # Draw the score information.
    sb.show_score()

    # Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()

    # Make the most recently drawn screen visible.
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, sb, ship, pirates, bullets):
    """Update position of bullets, and get rid of old bullets."""
    # Update bullet positions.
    bullets.update()

    # Get rid of bullets that have disappeared.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_pirate_collisions(ai_settings, screen, stats, sb, ship,
                                  pirates, bullets)


def check_high_score(stats, sb):
    """Check to see if there's a new high score."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def check_bullet_pirate_collisions(ai_settings, screen, stats, sb, ship,
                                  pirates, bullets):
    """Respond to bullet-pirate collisions."""
    # Remove any bullets and pirates that have collided.
    collisions = pygame.sprite.groupcollide(bullets, pirates, True, True)

    if collisions:
        for pirates in collisions.values():
            stats.score += ai_settings.pirate_points * len(pirates)
            sb.prep_score()
        check_high_score(stats, sb)

    if len(pirates) == 0:
        # If the entire fleet is destroyed, start a new level.
        bullets.empty()
        ai_settings.increase_speed()

        # Increase level.
        stats.level += 1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, pirates)


def check_fleet_edges(ai_settings, pirates):
    """Respond appropriately if any pirates have reached an edge."""
    for pirate in pirates.sprites():
        if pirate.check_edges():
            change_fleet_direction(ai_settings, pirates)
            break


def change_fleet_direction(ai_settings, pirates):
    """Drop the entire fleet, and change the fleet's direction."""
    for pirate in pirates.sprites():
        pirate.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, screen, stats, sb, ship, pirates, bullets):
    """Respond to ship being hit by pirate."""
    if stats.ships_left > 0:
        # Decrement ships_left.
        stats.ships_left -= 1

        # Update scoreboard.
        sb.prep_ships()

    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

    # Empty the list of pirates and bullets.
    pirates.empty()
    bullets.empty()

    # Create a new fleet, and center the ship.
    create_fleet(ai_settings, screen, ship, pirates)
    ship.center_ship()

    # Pause.
    sleep(0.5)


def check_pirates_bottom(ai_settings, screen, stats, sb, ship, pirates,
                        bullets):
    """Check if any pirates have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for pirate in pirates.sprites():
        if pirate.rect.bottom >= screen_rect.bottom:
            # Treat this the same as if the ship got hit.
            ship_hit(ai_settings, screen, stats, sb, ship, pirates, bullets)
            break


def update_pirates(ai_settings, screen, stats, sb, ship, pirates, bullets):
    """
    Check if the fleet is at an edge,
      then update the postions of all pirates in the fleet.
    """
    check_fleet_edges(ai_settings, pirates)
    pirates.update()

    # Look for pirate-ship collisions.
    if pygame.sprite.spritecollideany(ship, pirates):
        ship_hit(ai_settings, screen, stats, sb, ship, pirates, bullets)

    # Look for pirates hitting the bottom of the screen.
    check_pirates_bottom(ai_settings, screen, stats, sb, ship, pirates, bullets)


def get_number_pirates_x(ai_settings, pirate_width):
    """Determine the number of pirates that fit in a row."""
    available_space_x = ai_settings.screen_width - 2 * pirate_width
    number_pirates_x = int(available_space_x / (2 * pirate_width))
    return number_pirates_x


def get_number_rows(ai_settings, ship_height, pirate_height):
    """Determine the number of rows of pirates that fit on the screen."""
    available_space_y = (ai_settings.screen_height -
                         (3 * pirate_height) - ship_height)
    number_rows = int(available_space_y / (2 * pirate_height))
    return number_rows


def create_pirate(ai_settings, screen, pirates, pirate_number, row_number):
    """Create a pirate, and place it in the row."""
    pirate = Pirate(ai_settings, screen)
    pirate_width = pirate.rect.width
    pirate.x = pirate_width + 2 * pirate_width * pirate_number
    pirate.rect.x = pirate.x
    pirate.rect.y = pirate.rect.height + 2 * pirate.rect.height * row_number
    pirates.add(pirate)


def create_fleet(ai_settings, screen, ship, pirates):
    """Create a full fleet of pirates."""
    # Create a pirate, and find number of pirates in a row.
    pirate = Pirate(ai_settings, screen)
    number_pirates_x = get_number_pirates_x(ai_settings, pirate.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height,
                                  pirate.rect.height)

    # Create the fleet of pirates.
    for row_number in range(number_rows):
        for pirate_number in range(number_pirates_x):
            create_pirate(ai_settings, screen, pirates, pirate_number,
                         row_number)
