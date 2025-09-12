Promise.resolve().then(() => {
  //
  function getWrapped(currentYear) {
    const leagueId =
      new URL(window.document.location.href).searchParams.get("leagueId") ||
      203836968;
    function groupByF(ts, f) {
      return ts.reduce((prev, curr) => {
        const key = f(curr);
        if (!prev[key]) prev[key] = [];
        prev[key].push(curr);
        return prev;
      }, {});
    }
    function fromEntries(arr) {
      return Object.fromEntries(
        arr.filter((a) => a !== undefined).map((a) => [a.key, a.value])
      );
    }
    function clog(t) {
      console.log(t);
      return t;
    }
    return Promise.resolve()
      .then(() => [
        Promise.resolve().then(() => currentYear.toString()),
        Promise.resolve()
          .then(() =>
            fetch(
              `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/${currentYear}/segments/0/leagues/${leagueId}?view=kona_playercard`,
              {
                headers: {
                  accept: "application/json",
                  "x-fantasy-filter": JSON.stringify({
                    players: {
                      filterStatsForTopScoringPeriodIds: {
                        value: 17,
                        additionalValue: [
                          `00${currentYear}`,
                          `10${currentYear}`,
                        ],
                      },
                    },
                  }),
                  "x-fantasy-platform":
                    "kona-PROD-5b4759b3e340d25d9e1ae248daac086ea7c37db7",
                  "x-fantasy-source": "kona",
                },
                credentials: "include",
              }
            )
              .then((resp) => resp.json())
              .then((resp) => resp)
              .then((resp) =>
                resp.players
                  .map((player) => player.player)
                  .map((player) => ({
                    player,
                    seasonStats: player.stats.find(
                      (s) => s.scoringPeriodId === 0 && s.statSourceId === 0
                    ),
                  }))
                  .map(({ player, seasonStats }) => ({
                    id: player.id.toString(),
                    nflTeamId: player.proTeamId.toString(),
                    name: player.fullName,
                    position:
                      { 1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST" }[
                        player.defaultPositionId
                      ] || player.defaultPositionId.toString(),
                    total:
                      (seasonStats === null || seasonStats === void 0
                        ? void 0
                        : seasonStats.appliedTotal) || 0,
                    average:
                      (seasonStats === null || seasonStats === void 0
                        ? void 0
                        : seasonStats.appliedAverage) || 0,
                    scores: fromEntries(
                      player.stats
                        .filter(
                          (stat) =>
                            stat.seasonId === parseInt(currentYear) &&
                            stat.statSourceId === 0
                        )
                        .map((stat) => ({
                          key: stat.scoringPeriodId.toString(),
                          value: parseFloat(
                            (stat.appliedTotal || 0).toFixed(2)
                          ),
                        }))
                    ),
                    ownership: Object.fromEntries(
                      Object.entries(player.ownership || {}).filter(([k]) =>
                        [
                          "averageDraftPosition",
                          "auctionValueAverage",
                          "percentOwned",
                        ].includes(k)
                      )
                    ),
                    injuryStatus: player.injuryStatus,
                  }))
                  .filter((player) => {
                    var _player$ownership;
                    return (
                      Object.keys(player.ownership).length > 0 &&
                      (((_player$ownership = player.ownership) === null ||
                      _player$ownership === void 0
                        ? void 0
                        : _player$ownership.percentOwned) > 0.1 ||
                        Object.values(player.scores).filter((s) => s !== 0)
                          .length > 0)
                    );
                  })
                  .map(({ ...player }) => ({ key: player.id, value: player }))
              )
              .then((playersArr) => fromEntries(playersArr))
          )
          .then((players) => players),
        Promise.resolve()
          .then(() =>
            fetch(
              `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/${currentYear}/segments/0/leagues/${leagueId}?view=mDraftDetail&view=mRoster`,
              { credentials: "include" }
            )
              .then((resp) => resp.json())
              .then((resp) =>
                Promise.resolve()
                  .then(() =>
                    Array.from(new Array(resp.status.latestScoringPeriod))
                      .map((_, i) => i + 1)
                      .map((weekNum) =>
                        fetch(
                          `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/${currentYear}/segments/0/leagues/${leagueId}?view=mScoreboard&scoringPeriodId=${weekNum}`,
                          { credentials: "include" }
                        )
                          .then((resp) => resp.json())
                          .then((resp) =>
                            Promise.resolve()
                              .then(() =>
                                resp.teams.map((team) => ({
                                  id: team.id.toString(),
                                  name: team.name,
                                  schedule: {
                                    weekNum,
                                    ...resp.schedule
                                      .flatMap((matchup) => [
                                        matchup.home,
                                        matchup.away,
                                      ])
                                      .find(
                                        (s) =>
                                          (s === null || s === void 0
                                            ? void 0
                                            : s.rosterForCurrentScoringPeriod) &&
                                          s.teamId === team.id
                                      ),
                                  },
                                }))
                              )
                              .then((week) =>
                                fromEntries(
                                  week.map((team) => ({
                                    key: team.id,
                                    value: team,
                                  }))
                                )
                              )
                          )
                      )
                  )
                  .then((ps) => Promise.all(ps))
                  .then((weeks) =>
                    Object.values(weeks[0] || {}).map((team) => ({
                      id: team.id,
                      name: team.name,
                      draft: resp.draftDetail.picks
                        .map((p, pickIndex) => ({ ...p, pickIndex }))
                        .filter((p) => p.teamId === parseInt(team.id))
                        .map(({ playerId, pickIndex }) => ({
                          playerId,
                          pickIndex,
                        })),
                      pickOrder: resp.settings.draftSettings.pickOrder.indexOf(
                        parseInt(team.id)
                      ),
                      rosters: fromEntries(
                        weeks
                          .map((week) => week[team.id].schedule)
                          .filter((s) => s.rosterForCurrentScoringPeriod)
                          .map((s) => ({
                            weekNum: s.weekNum.toString(),
                            starting: s.rosterForCurrentScoringPeriod.entries
                              .filter((e) => ![20, 21].includes(e.lineupSlotId))
                              .map((e) => e.playerId.toString()),
                            rostered:
                              s.rosterForCurrentScoringPeriod.entries.map((e) =>
                                e.playerId.toString()
                              ),
                          }))
                          .concat({
                            weekNum: "0",
                            starting: [],
                            rostered: resp.teams
                              .find((t) => t.id.toString() === team.id)
                              .roster.entries.map((e) => e.playerId.toString()),
                          })
                          .map((roster) => ({
                            key: roster.weekNum,
                            value: roster,
                          }))
                      ),
                    }))
                  )
              )
              .then((teams) =>
                fromEntries(
                  teams.map((team) => ({ key: team.id, value: team }))
                )
              )
          )
          .then((teams) => teams),
        Promise.resolve()
          .then(() =>
            fetch(
              `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/${currentYear}/segments/0/leagues/${leagueId}?view=mMatchupScore&view=mSettings`,
              { credentials: "include" }
            )
              .then((resp) => resp.json())
              .then((resp) =>
                Array.from(
                  new Array(resp.settings.scheduleSettings.matchupPeriodCount)
                )
                  .map((_, i) => i + 1)
                  .map((matchupPeriodId) => ({
                    key: matchupPeriodId.toString(),
                    value: resp.schedule
                      .filter((s) => s.matchupPeriodId === matchupPeriodId)
                      .map((s) =>
                        [s.home, s.away].map((t) =>
                          t === null || t === void 0
                            ? void 0
                            : t.teamId.toString()
                        )
                      ),
                  }))
              )
              .then((matchups) => fromEntries(matchups))
          )
          .then((ffMatchups) => ffMatchups),
        Promise.resolve()
          .then(() =>
            fetch(
              `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/${currentYear}?view=proTeamSchedules_wl`,
              { credentials: "include" }
            )
              .then((resp) => resp.json())
              .then((resp) =>
                resp.settings.proTeams.map((p) => ({
                  id: p.id.toString(),
                  name: p.name,
                  byeWeek: p.byeWeek,
                  proGamesByScoringPeriod: fromEntries(
                    Object.entries(p.proGamesByScoringPeriod)
                      .filter(([_, o]) => o[0].statsOfficial)
                      .map(([scoringPeriod, o]) => ({
                        key: scoringPeriod,
                        value: o[0].id,
                      }))
                  ),
                }))
              )
              .then((nflTeams) =>
                Promise.resolve()
                  .then(() =>
                    nflTeams.flatMap((team) =>
                      Object.values(team.proGamesByScoringPeriod)
                    )
                  )
                  .then((gameIds) =>
                    Object.keys(
                      fromEntries(
                        gameIds.map((gameId) => ({
                          key: gameId.toString(),
                          value: true,
                        }))
                      )
                    )
                  )
                  .then((gameIds) =>
                    gameIds.map((gameId) =>
                      fetch(
                        `https://www.espn.com/nfl/playbyplay/_/gameId/${gameId}`
                      )
                        .then((resp) => resp.text())
                        .then(
                          (resp) =>
                            resp.match(
                              /window\['__espnfitt__'\]=(.*?);<\/script>/
                            )[1]
                        )
                        .then((resp) => JSON.parse(resp))
                        .then((resp) => ({
                          fieldGoals: resp.page.content.gamepackage.scrSumm
                            .flatMap(({ items }) => items)
                            .filter((item) => item.typeAbbreviation === "FG")
                            .map((item) => ({
                              teamId: item.teamId,
                              yards: parseInt(
                                item.playText.match(
                                  /(\d+) (?:yard|yrd|yd) field goal/i
                                )[1]
                              ),
                            })),
                          punts: groupByF(
                            resp.page.content.gamepackage.allPlys
                              .flatMap(({ items }) => items)
                              .filter((p) => p.headline === "Punt")
                              .map((p) => ({
                                teamId: Object.values(
                                  resp.page.content.gamepackage.prsdTms
                                ).find((t) => t.displayName === p.teamName).id,
                                punt: (p.plays || [])
                                  .map((p) =>
                                    p.description.match(
                                      /(\S*) punts (\d+) yards? to \S+ (\d+)?/
                                    )
                                  )
                                  .find((p) => p),
                              }))
                              .filter((p) => {
                                var _p$punt;
                                return (_p$punt = p.punt) === null ||
                                  _p$punt === void 0
                                  ? void 0
                                  : _p$punt[0];
                              })
                              .map((p) => ({
                                ...p,
                                landed: !p.punt[3] ? 0 : parseInt(p.punt[3]),
                                punter: p.punt[1],
                                distance: parseInt(p.punt[2]),
                              })),
                            (p) => p.teamId
                          ),
                          drives: Object.fromEntries(
                            Object.values(
                              resp.page.content.gamepackage.prsdTms
                            ).map(({ id, displayName }) => [
                              id,
                              resp.page.content.gamepackage.allPlys
                                .flatMap(({ items }) => items)
                                .filter((p) => p.teamName === displayName)
                                .map((drive) => drive.headline),
                            ])
                          ),
                        }))
                        .then((value) => ({ key: gameId.toString(), value }))
                    )
                  )
                  .then((ps) => Promise.all(ps))
                  .then((gamesByGameId) => fromEntries(gamesByGameId))
                  .then((gamesByGameId) =>
                    fetch(
                      `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/${currentYear}/segments/0/leagues/${leagueId}?view=kona_playercard`,
                      {
                        headers: {
                          accept: "application/json",
                          "x-fantasy-filter": JSON.stringify({
                            players: {
                              filterSlotIds: { value: [16] },
                              filterStatsForTopScoringPeriodIds: { value: 17 },
                            },
                          }),
                          "x-fantasy-platform":
                            "kona-PROD-5b4759b3e340d25d9e1ae248daac086ea7c37db7",
                          "x-fantasy-source": "kona",
                        },
                        credentials: "include",
                      }
                    )
                      .then((resp) => resp.json())
                      .then((resp) =>
                        Object.keys(
                          fromEntries(
                            resp.players
                              .flatMap((player) => player.player.stats)
                              .map((s) => ({
                                key: s.scoringPeriodId.toString(),
                                value: true,
                              }))
                          )
                        ).map((scoringPeriodId) => ({
                          key: scoringPeriodId.toString(),
                          value: fromEntries(
                            resp.players
                              .map((player) => {
                                var _player$player$stats$;
                                return {
                                  teamId: player.player.proTeamId,
                                  stats:
                                    (_player$player$stats$ =
                                      player.player.stats.find(
                                        (s) =>
                                          s.scoringPeriodId.toString() ===
                                          scoringPeriodId
                                      )) === null ||
                                    _player$player$stats$ === void 0
                                      ? void 0
                                      : _player$player$stats$.stats,
                                };
                              })
                              .map(({ teamId, stats }) =>
                                stats === undefined
                                  ? undefined
                                  : {
                                      key: teamId.toString(),
                                      value: {
                                        yardsAllowed: stats["127"] || 0,
                                        pointsAllowed: stats["187"] || 0,
                                      },
                                    }
                              )
                          ),
                        }))
                      )
                      .then((defensesByScoringPeriod) =>
                        fromEntries(defensesByScoringPeriod)
                      )
                      .then((defensesByScoringPeriod) =>
                        nflTeams
                          .map(({ proGamesByScoringPeriod, ...team }) => ({
                            ...team,
                            nflGamesByScoringPeriod: fromEntries(
                              Object.entries(proGamesByScoringPeriod)
                                .filter(
                                  ([scoringPeriod]) =>
                                    defensesByScoringPeriod[scoringPeriod] !==
                                    undefined
                                )
                                .map(([scoringPeriod, gameId]) => ({
                                  key: scoringPeriod,
                                  value: {
                                    opp: Object.keys(
                                      gamesByGameId[gameId].drives
                                    ).find((t) => t !== team.id),
                                    drives:
                                      gamesByGameId[gameId].drives[team.id],
                                    fieldGoals: gamesByGameId[gameId].fieldGoals
                                      .filter((play) => play.teamId === team.id)
                                      .map((play) => play.yards),
                                    punts: (
                                      gamesByGameId[gameId].punts[team.id] || []
                                    ).flatMap((play) => ({
                                      landed: play.landed,
                                      distance: play.distance,
                                    })),
                                    punter: Object.keys(
                                      groupByF(
                                        gamesByGameId[gameId].punts[team.id] ||
                                          [],
                                        (p) => p.punter
                                      )
                                    ).join(","),
                                    ...defensesByScoringPeriod[scoringPeriod][
                                      team.id
                                    ],
                                  },
                                }))
                            ),
                          }))
                          .map((team) => ({ key: team.id, value: team }))
                      )
                  )
                  .then((nflTeams) => fromEntries(nflTeams))
              )
          )
          .then((nflTeams) => nflTeams),
        Promise.resolve()
          .then(() =>
            fetch(
              "https://api.fantasycalc.com/values/current?isDynasty=false&numQbs=2&numTeams=10&ppr=1&includeAdp=false"
            )
              .then((resp) => resp.json())
              .then((resp) =>
                Object.fromEntries(
                  resp.map((p) => [
                    p.player.espnId
                      ? p.player.espnId.toString()
                      : p.player.name,
                    p.redraftValue / 100,
                  ])
                )
              )
          )
          .then((players) => ({ players, timestamp: Date.now() })),
      ])
      .then((ps) => Promise.all(ps))
      .then(
        ([year, nflPlayers, ffTeams, ffMatchups, nflTeams, fantasyCalc]) => ({
          year,
          nflPlayers,
          ffTeams,
          ffMatchups,
          nflTeams,
          fantasyCalc,
        })
      )
      .then(clog);
  }
  //
  return getWrapped("2025");
});
