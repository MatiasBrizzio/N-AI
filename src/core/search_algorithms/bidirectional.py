# src/core/search_algorithms/bidirectional.py
infinity = float('inf')

# ______________________________________________________________________________
# Bidirectional Search
# Pseudocode from https://webdocs.cs.ualberta.ca/%7Eholte/Publications/MM-AAAI2016.pdf

def bidirectional_search(problem):
    e = problem.find_min_edge()
    g_f, gg_b = {problem.initial : 0}, {problem.goal : 0}
    open_f, open_b = [problem.initial], [problem.goal]
    closed_f, closed_b = [], []
    U = infinity


    def extend(U, open_dir, open_other, g_dir, g_other, closed_dir):
        """Extend search in given direction"""
        n = find_key(C, open_dir, g_dir)

        open_dir.remove(n)
        closed_dir.append(n)

        for c in problem.actions(n):
            if c in open_dir or c in closed_dir:
                if g_dir[c] <= problem.path_cost(g_dir[n], n, None, c):
                    continue

                open_dir.remove(c)

            g_dir[c] = problem.path_cost(g_dir[n], n, None, c)
            open_dir.append(c)

            if c in open_other:
                U = min(U, g_dir[c] + g_other[c])

        return U, open_dir, closed_dir, g_dir


    def find_min(open_dir, g):
        """Finds minimum priority, g and f values in open_dir"""
        m, m_f = infinity, infinity
        for n in open_dir:
            f = g[n] + problem.h(n)
            pr = max(f, 2*g[n])
            m = min(m, pr)
            m_f = min(m_f, f)

        return m, m_f, min(g.values())


    def find_key(pr_min, open_dir, g):
        """Finds key in open_dir with value equal to pr_min
        and minimum g value."""
        m = infinity
        state = -1
        for n in open_dir:
            pr = max(g[n] + problem.h(n), 2*g[n])
            if pr == pr_min:
                if g[n] < m:
                    m = g[n]
                    state = n

        return state


    while open_f and open_b:
        pr_min_f, f_min_f, g_min_f = find_min(open_f, g_f)
        pr_min_b, f_min_b, g_min_b = find_min(open_b, gg_b)
        C = min(pr_min_f, pr_min_b)

        if U <= max(C, f_min_f, f_min_b, g_min_f + g_min_b + e):
            return U

        if C == pr_min_f:
            # Extend forward
            U, open_f, closed_f, g_f = extend(U, open_f, open_b, g_f, gg_b, closed_f)
        else:
            # Extend backward
            U, open_b, closed_b, gg_b = extend(U, open_b, open_f, gg_b, g_f, closed_b)

    return infinity

