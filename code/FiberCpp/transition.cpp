/**
* @file		transition.cpp
* @brief	Source file for the transition class
* @author	Ken Campbell
*/

#include <cstdio>

#include "transition.h"
#include "m_state.h"
#include "kinetic_scheme.h"
#include "FiberSim_model.h"
#include "global_definitions.h"
#include "JSON_functions.h"

#include "rapidjson\document.h"

#include "gsl_vector.h"
#include "gsl_math.h"


// Constructor
transition::transition(const rapidjson::Value& tr, m_state* set_p_parent_m_state)
{
	// Set p_parent_m_state
	p_parent_m_state = set_p_parent_m_state;

	// Set transition_type to unknown - will be set later on
	transition_type = 'x';

	JSON_functions::check_JSON_member_int(tr, "new_state");
	new_state = tr["new_state"].GetInt();

	JSON_functions::check_JSON_member_string(tr, "rate_type");
	sprintf_s(rate_type, _MAX_PATH, tr["rate_type"].GetString());

	// Read in parameters
	JSON_functions::check_JSON_member_array(tr, "rate_parameters");
	const rapidjson::Value& rp = tr["rate_parameters"];

	rate_parameters = gsl_vector_alloc(MAX_NO_OF_RATE_PARAMETERS);
	gsl_vector_set_zero(rate_parameters);

	for (int i = 0; i < (int)rp.Size(); i++)
	{
		gsl_vector_set(rate_parameters, i, rp[i].GetDouble());
	}
}

transition::transition()
{
	// Default constructor - used if there is no defined transition
	new_state = 0;
	transition_type = 'x';
	sprintf_s(rate_type, _MAX_PATH, "");
	rate_parameters = gsl_vector_alloc(MAX_NO_OF_RATE_PARAMETERS);
	gsl_vector_set_zero(rate_parameters);
}

// Destructor
transition::~transition(void)
{
	// Tidy up
	gsl_vector_free(rate_parameters);
}

// Functions

double transition::calculate_rate(double x, double node_force, int mybpc_state)
{
	//! Returns the rate for a transition with a given x

	// Variables
	double rate = 0.0;

	// Code

	// Constant
	if (!strcmp(rate_type, "constant"))
	{
		rate = gsl_vector_get(rate_parameters, 0);
	}

	if (!strcmp(rate_type, "MyBPC_dependent"))
	{
		rate = gsl_vector_get(rate_parameters, 0);
		
		if (mybpc_state == 1)
		{
			rate = rate * gsl_vector_get(rate_parameters, 1);
		}
	}

	// Force-dependent
	if (~strcmp(rate_type, "force_dependent"))
	{
		rate = gsl_vector_get(rate_parameters, 0) *
			(1.0 + (node_force * gsl_vector_get(rate_parameters, 1)));
	}

	// Gaussian
	if (!strcmp(rate_type, "gaussian"))
	{
		FiberSim_model* p_model = p_parent_m_state->p_parent_scheme->p_fs_model;
		double k_cb = p_model->m_k_cb;

		rate = gsl_vector_get(rate_parameters, 0) *
			exp(-(0.5 * k_cb * gsl_pow_int(x, 2)) /
			(1e18 * 1.38e-23 * 310.0));
	}

	// Poly
	if (!strcmp(rate_type, "poly"))
	{
		rate = gsl_vector_get(rate_parameters, 0) +
			(gsl_vector_get(rate_parameters, 1) *
				gsl_pow_int(x, (int)gsl_vector_get(rate_parameters, 2)));
	}

	// Curtail at max rate
	FiberSim_options* p_options = p_parent_m_state->p_parent_scheme->p_fs_options;
	if (rate > (p_options->max_rate))
		rate = p_options->max_rate;

	if (rate < 0.0)
		rate = 0.0;

	// Return
	return rate;
}

