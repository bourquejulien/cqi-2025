package server

import (
	"context"
	"cqiprog/data"
	"cqiprog/scheduler"
	"fmt"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/render"
)

type Server struct {
	Data      *data.Data
	Scheduler *scheduler.Scheduler

	InternalKey string

	router *chi.Mux
	server http.Server
}

func (p *Server) Init() {
	router := chi.NewRouter()
	router.Use(middleware.Logger)

	router.Route("/api", func(r chi.Router) {
		r.Route("/game", func(r chi.Router) {
			r.Get("/list", p.listGames)
			r.Get("/get", p.getGame)
		})
		r.Get("/stats", p.getStats)

		r.Route("/internal", func(r chi.Router) {
			r.Use(p.validateToken)
			r.Route("/match", func(r chi.Router) {
				r.Post("/reset", p.resetMatchResults)
				r.Post("/pop", p.popMatch)
				r.Post("/add_result", p.addMatchResults)
			})
			r.Post("/autoplay", p.manageAutoplay)
			r.Post("/force_queue", p.forceQueueMatch)
		})
	})

	p.router = router
}

func (p *Server) Start(port int) error {
	address := fmt.Sprintf("0.0.0.0:%d", port)

	p.server = http.Server{Addr: address, Handler: p.router}
	if err := p.server.ListenAndServe(); err != nil {
		return err
	}

	return nil
}

func (p *Server) Stop(ctx context.Context) error {
	return p.server.Shutdown(ctx)
}

func (p *Server) listGames(w http.ResponseWriter, r *http.Request) {
	limit, err := strconv.Atoi(r.URL.Query().Get("limit"))
	if err != nil {
		http.Error(w, "Invalid limit parameter", http.StatusBadRequest)
		return
	}

	page, err := strconv.Atoi(r.URL.Query().Get("page"))
	if err != nil {
		http.Error(w, "Invalid page parameter", http.StatusBadRequest)
		return
	}

	games, err := p.Data.ListGames(r.Context(), limit, page)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	render.JSON(w, r, games)
}

func (p *Server) getGame(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	if id == "" {
		http.Error(w, "Invalid id parameter", http.StatusBadRequest)
		return
	}

	game, err := p.Data.GetGame(r.URL.Query().Get("id"), r.Context())

	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	render.JSON(w, r, game)
}

func (p *Server) getStats(w http.ResponseWriter, r *http.Request) {
	// TODO
	stats := Stats{}
	render.JSON(w, r, stats)
}

func (p *Server) resetMatchResults(w http.ResponseWriter, r *http.Request) {
	p.Scheduler.Reset()
}

func (p *Server) popMatch(w http.ResponseWriter, r *http.Request) {
	n, err := strconv.Atoi(r.URL.Query().Get("n"))

	if err != nil {
		http.Error(w, "Invalid n parameter", http.StatusBadRequest)
		return
	}

	matches := p.Scheduler.PopMatch(n, r.Context())

	resultMatches := make([]Match, len(matches))
	for i, match := range matches {
		resultMatches[i] = Match{
			Id:         match.Id,
			Team1Id:    match.Team1Id,
			Team2Id:    match.Team2Id,
			ImageTeam1: match.ImageTeam1,
			ImageTeam2: match.ImageTeam2,
		}
	}

	render.JSON(w, r, resultMatches)
}

func (p *Server) addMatchResults(w http.ResponseWriter, r *http.Request) {
	var result scheduler.GameResult
	if err := render.DecodeJSON(r.Body, &result); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if !p.Scheduler.AddResult(&result, r.Context()) {
		http.Error(w, "Invalid game response", http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func (p *Server) manageAutoplay(w http.ResponseWriter, r *http.Request) {
	isEnabled, err := strconv.ParseBool(r.URL.Query().Get("enabled"))
	if err != nil {
		http.Error(w, "Invalid enabled parameter", http.StatusBadRequest)
		return
	}

	p.Scheduler.SetAutoplay(isEnabled)
}

func (p *Server) forceQueueMatch(w http.ResponseWriter, r *http.Request) {
	team1Id := r.URL.Query().Get("team1_id")
	team2Id := r.URL.Query().Get("team2_id")

	if team1Id == "" || team2Id == "" {
		http.Error(w, "Invalid team1_id or team2_id parameter", http.StatusBadRequest)
		return
	}

	p.Scheduler.ForceAddMatch(team1Id, team2Id, r.Context())
}

func (p *Server) validateToken(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := r.Header.Get("Authorization")
		if token != p.InternalKey {
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}
		next.ServeHTTP(w, r)
	})
}
