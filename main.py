""" test script agent in pycoq 
"""
import asyncio
import os

from typing import Iterable

import pycoq.opam
import pycoq.common
import pycoq.agent

async def query_proof(coq) -> str:
    """
    sends serapi command
    (Query () Definition name)
    """
    cmd_tag = len(coq._sent_history)
    cmd = f'(Query ((PpStr)) Proof)'
    await coq._kernel.writeline(cmd)
    print('writen')
    coq._sent_history.append(cmd)
    return cmd_tag

async def query_proof_completed(coq):
    cmd_tag = await query_proof(coq)
    print('queries')
    resp_ind = await coq.wait_for_answer_completed(cmd_tag)
    print('waited')
    coqexns = await coq.coqexns(cmd_tag)
    print('exns')
    if coqexns != []:
        raise RuntimeError(f'Unexpected error during coq-serapi command Query () Goals '
                           f'with CoqExns {coqexns}')
    goals = await coq._answer(cmd_tag)
    return goals

async def tutorial_deterministic_agent(theorems: Iterable):
    """
    a snipped of code demonstrating usage of pycoq
    """

    # create default coq context for evaluation of a theorem
    coq_ctxt = pycoq.common.CoqContext(pwd=os.getcwd(),
                                       executable='',
                                       target='serapi_shell')
    cfg = pycoq.opam.opam_serapi_cfg(coq_ctxt)
    # bytearray(b'[ERROR] The selected switch ocaml-variants.4.07.1+flambda_coq-serapi.8.11.0+0.11.1 is not installed.\n')
    # create python coq-serapi object that wraps API of the coq-serapi
    async with pycoq.serapi.CoqSerapi(cfg) as coq:
        for prop, script in theorems:
            cmd_tag, resp_ind, coq_exc, sid = await coq.execute(prop)
            if coq_exc:
                print(f"{prop} raised coq exception {coq_exc}")
                continue
            for stmt in script:
                print(f"executing: {stmt}")
                _, _, coq_exc, _ = await coq.execute(stmt)

                if coq_exc:
                    print(f"evaluation of {stmt} in coq-serapi session raised exception {coq_exc}")
                    break

                serapi_goals = await coq.serapi_goals()
                serapi_proofs = await query_proof_completed(coq)
                print(serapi_proofs)
        # for prop, script in theorems:
        #
        #     # execute proposition of the theorem
        #     cmd_tag, resp_ind, coq_exc, sid = await coq.execute(prop)
        #     if coq_exc:
        #         print(f"{prop} raised coq exception {coq_exc}")
        #         continue
        #
        #     # execute the proof script of the theorem
        #     n_steps, n_goals = await pycoq.agent.script_agent(coq, script)
        #
        #     msg = f"Proof {script} fail" if n_goals != 0 else f"Proof {script} success"
        #     print(f"{prop} ### {msg} in {n_steps} steps\n")

def main():
    # pycoq.opam.opam_install_serapi()
    # theorems = [
    #     ("Theorem th4: forall A B C D: Prop, A->(A->B)->(B->C)->(C->D)->D.",
    #      ["auto."]),
    #     ("Theorem th5: forall A B C D E: Prop, A->(A->B)->(B->C)->(C->D)->E.",
    #      ["auto."]),
    #     ("Theorem th6: forall A B C D E: Prop, A->(A->B)->(B->C)->(C->D)->(D->E)->E.",
    #      ["auto."])]
    theorems = [
        ("Theorem add_easy: forall n:nat, 0 + n = n.",
         ["intros.", "Show Proof.", "simpl.", "Show Proof.", "reflexivity.", "Show Proof."]),
    ]

    asyncio.run(tutorial_deterministic_agent(theorems))


if __name__ == '__main__':
    main()
