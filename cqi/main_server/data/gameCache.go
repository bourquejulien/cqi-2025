package data

import (
	"slices"
	"sort"
	"time"
)

const (
	LIST_CACHE_SIZE = 1000
	GAME_CACHE_SIZE = 200
)

func (p *cache) cleanup() {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if len(p.list) > LIST_CACHE_SIZE {
		p.list = p.list[:LIST_CACHE_SIZE]
	}

	if len(p.mapping) < GAME_CACHE_SIZE {
		return
	}

	for _, game := range slices.Backward(p.list) {
		if len(p.mapping) <= GAME_CACHE_SIZE/2 {
			break
		}

		delete(p.mapping, game.Id)
	}
}

func (p *cache) getGame(id string) *DbGame {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if game, ok := p.mapping[id]; ok {
		return game
	}

	return nil
}

func (p *cache) addGame(game *DbGame) {
	p.lock.Lock()
	defer p.lock.Unlock()

	p.mapping[game.Id] = game
	p.list = append(p.list, game)

	sort.Slice(p.list, func(i, j int) bool {
		return p.list[i].EndTime.After(p.list[j].EndTime)
	})
}

func (p *cache) getGamesSince(time time.Time) []*DbGame {
	p.lock.RLock()
	defer p.lock.RUnlock()

	var games []*DbGame
	for _, game := range p.list {
		if game.EndTime.After(time) {
			games = append(games, game)
		}
	}

	return games
}

func (p *cache) getGameList(limit, page int) (bool, []*DbGame) {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if len(p.list) >= limit*(page+1) {
		return true, p.list[limit*page : limit*page+limit]
	}

	return false, nil
}

func (p *cache) addGameList(games []*DbGame, offset int) {
	p.lock.Lock()
	defer p.lock.Unlock()

	if len(p.list) >= LIST_CACHE_SIZE || offset > len(p.list) || offset+len(games) <= len(p.list) {
		return
	}

	p.list = append(p.list[0:offset], games...)
}
