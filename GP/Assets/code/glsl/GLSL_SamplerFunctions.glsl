#define NUMMASKS 10

uniform sampler2D SurfaceMaskSampler; // only for surfaces.
uniform sampler2D SurfacePixframeSampler; // only for surfaces.


float isInRange(float a , float b , float c)
{ return min((1.0-step(c, a)) , step(b, a)); }

float map(float value, float inMin, float inMax, float outMin, float outMax) {
  return outMin + (outMax - outMin) * (value - inMin) / (inMax - inMin);
}

vec3 map(vec3 value, float inMin, float inMax, float outMin, float outMax) {
  
	vec3 returnVec = vec3(
		outMin + (outMax - outMin) * (value.r - inMin) / (inMax - inMin),
		outMin + (outMax - outMin) * (value.g - inMin) / (inMax - inMin),
		outMin + (outMax - outMin) * (value.b - inMin) / (inMax - inMin)
		);
	return returnVec;
}

struct ProjectorObject
{
	mat4 	vm;
	mat4 	pm;

	float 	Pscale;
	int 	Pstyle;
	int 	Pextend;

	int 	Routingr;
	int 	Routingg;
	int 	Routingb;
	int 	Routinga;

	int 	NumMasksR;
	int 	NumMasksG;
	int 	NumMasksB;
	int 	NumMasksA;

	int 	Masks_r[NUMMASKS];
	int 	Masks_g[NUMMASKS];
	int 	Masks_b[NUMMASKS];
	int 	Masks_a[NUMMASKS];

	float 	Setcolorr;
	float 	Setcolorg;
	float 	Setcolorb;
	float 	Setcolora;

	bool 	Projectoractive;

	float 	Gamma;
	float 	Gain;
	float 	Uvfxorigin;
	float 	Uvfxshuffle;
	int 	Projectorblendmode;
	int 	Projectorlayer;
	int 	Coordinateset;
};


ProjectorObject GetProjector( int projectorIndex ){
	/*
	This function given a projector index, will assemble the data into a Projector struct, and return it.
	*/
	ProjectorObject Proj;

	int ProjectorStartingOffset = projectorIndex * ProjectorBufferSize;
	Proj.vm = mat4(0);
	Proj.pm = mat4(0);
	int row=0; int col=0;
	for( int i=0; i<16; i++ )
	{
		col = i % 4;
		row = i / 4;
		Proj.vm[row][col] = texelFetch(Proj_Params, ProjectorStartingOffset+i).x;
		
		col = i % 4;
		row = i / 4;
		Proj.pm[row][col] = texelFetch(Proj_Params, ProjectorStartingOffset+i+16).x;
	}

	Proj.Pscale = texelFetch(Proj_Params, ProjectorStartingOffset+32).x;
	Proj.Pstyle = int(texelFetch(Proj_Params, ProjectorStartingOffset+33).x);
	Proj.Pextend = int(texelFetch(Proj_Params, ProjectorStartingOffset+34).x);

	Proj.Routingr = int(texelFetch(Proj_Params, ProjectorStartingOffset+35).x);
	Proj.Routingg = int(texelFetch(Proj_Params, ProjectorStartingOffset+36).x);
	Proj.Routingb = int(texelFetch(Proj_Params, ProjectorStartingOffset+37).x);
	Proj.Routinga = int(texelFetch(Proj_Params, ProjectorStartingOffset+38).x);

	Proj.NumMasksR = int(texelFetch(Proj_Params, ProjectorStartingOffset+39).x);
	Proj.NumMasksG = int(texelFetch(Proj_Params, ProjectorStartingOffset+40).x);
	Proj.NumMasksB = int(texelFetch(Proj_Params, ProjectorStartingOffset+41).x);
	Proj.NumMasksA = int(texelFetch(Proj_Params, ProjectorStartingOffset+42).x);

	for( int i=0; i<10; i++ ){
		Proj.Masks_r[i] = int(texelFetch(Proj_Params, ProjectorStartingOffset+60+i).x);
	}
	for( int i=0; i<10; i++ ){
		Proj.Masks_g[i] = int(texelFetch(Proj_Params, ProjectorStartingOffset+70+i).x);
	}
	for( int i=0; i<10; i++ ){
		Proj.Masks_b[i] = int(texelFetch(Proj_Params, ProjectorStartingOffset+80+i).x);
	}
	for( int i=0; i<10; i++ ){
		Proj.Masks_a[i] = int(texelFetch(Proj_Params, ProjectorStartingOffset+90+i).x);
	}

	Proj.Setcolorr = texelFetch(Proj_Params, ProjectorStartingOffset+43).x;
	Proj.Setcolorg = texelFetch(Proj_Params, ProjectorStartingOffset+44).x;
	Proj.Setcolorb = texelFetch(Proj_Params, ProjectorStartingOffset+45).x;
	Proj.Setcolora = texelFetch(Proj_Params, ProjectorStartingOffset+46).x;

	Proj.Projectoractive = bool(texelFetch(Proj_Params, ProjectorStartingOffset+47).x);

	Proj.Gamma = texelFetch(Proj_Params, ProjectorStartingOffset+48).x;
	Proj.Gain = texelFetch(Proj_Params, ProjectorStartingOffset+49).x;
	Proj.Projectorblendmode = int(texelFetch(Proj_Params, ProjectorStartingOffset+50).x);

	// we may not need this in shader, since we are sorting our projectors in TD.
	Proj.Projectorlayer = int(texelFetch(Proj_Params, ProjectorStartingOffset+51).x);
	
	Proj.Coordinateset = int(texelFetch(Proj_Params, ProjectorStartingOffset+52).x);


	return Proj;
}


vec4 WorldSpace_to_ProjectorSpace( vec4 WorldSpaceCoords , float CoordIndex , ProjectorObject pObj ){

	float PreMask = 1;

	// xform WS coordinates to projector space.
	pObj.vm 				= inverse(pObj.vm);
	vec4 Coords_VS 			= pObj.vm * WorldSpaceCoords;
	vec4 Coords_PS 			= pObj.pm * Coords_VS;
	
	// test if z coordinate is in front of camera or not - must do before perspective divide! it makes everything +
	float inFrontOfCamera = float(Coords_PS.z > -1);

	if(pObj.Pstyle == 0){ // if perspective mode!
		Coords_PS.xyz /= Coords_PS.w; // do perspective divide.
	}
	
	Coords_PS.xyz = Coords_PS.xyz * .5 + .5; // NDC to 0:1 space

	// if projector style is chase projector:
	if(pObj.Pstyle == 2){

		// go ahead and mask to extents of projection cube no matter what extend mode.
		PreMask = min( isInRange( Coords_PS.x , 0 , 1 ) , PreMask);
		PreMask = min( isInRange( Coords_PS.y , 0 , 1 ) , PreMask);
		
		// now that we have thee mask based on real coords, lets modify coords for 1d chase.
		// we use a map function and Pscale, any coords that still fall outside of 0:1 will be 
		// treated the same as other projector modes, via extend, cycle, mirror, etc.
		Coords_PS.x = map( CoordIndex , 0 , pObj.Pscale , 0 , 1 );
		Coords_PS.y = 0.5;
		Coords_PS.z = 0.5;
	}

	// breaking the rules a bit, storing the in front / behind mask in W since we won't use it again.
	Coords_PS.w = inFrontOfCamera * PreMask;

	return Coords_PS;
}

float Cull_Pix_Against_Projector( vec4 ProjectorSpaceCoords , ProjectorObject pObj , int UtilizationMask ){

	float mask = 1;

	// composite the mask created earlier before perspective divide, that tells us if a Pix is infront of projector or not.
	mask = min( mask , ProjectorSpaceCoords.w );

	// IF projector is set to zero, for extend mode, also cull out pix outside left/right/top/bottom of frustum.
	if ( pObj.Pextend == 0 ){
		mask = min( isInRange( ProjectorSpaceCoords.x , 0 , 1 ) , mask);
		mask = min( isInRange( ProjectorSpaceCoords.y , 0 , 1 ) , mask);
	}

	return min( mask , UtilizationMask );
	// return ProjectorSpaceCoords.w;
}

vec4 Sample_Projector_Texture( vec4 ProjectorSpaceCoords , float ProjectorMask , int TextureID , float FadeScale ){

	
	if( TextureID >= 0 ){
		// sample the actual texture now that are coords are in the right place.
		int inputID = TextureID+2;
		vec4 ProjectedTexture = vec4(0);

		if(inputID == 2){ ProjectedTexture = texture(ProjTex0, ProjectorSpaceCoords.st); }
		if(inputID == 3){ ProjectedTexture = texture(ProjTex1, ProjectorSpaceCoords.st); }
		if(inputID == 4){ ProjectedTexture = texture(ProjTex2, ProjectorSpaceCoords.st); }
		if(inputID == 5){ ProjectedTexture = texture(ProjTex3, ProjectorSpaceCoords.st); }
		if(inputID == 6){ ProjectedTexture = texture(ProjTex4, ProjectorSpaceCoords.st); }
		if(inputID == 7){ ProjectedTexture = texture(ProjTex5, ProjectorSpaceCoords.st); }
		if(inputID == 8){ ProjectedTexture = texture(ProjTex6, ProjectorSpaceCoords.st); }
		if(inputID == 9){ ProjectedTexture = texture(ProjTex7, ProjectorSpaceCoords.st); }
		if(inputID == 10){ ProjectedTexture = texture(ProjTex8, ProjectorSpaceCoords.st); }
		if(inputID == 11){ ProjectedTexture = texture(ProjTex9, ProjectorSpaceCoords.st); }
		if(inputID == 12){ ProjectedTexture = texture(ProjTex10, ProjectorSpaceCoords.st); }
		if(inputID == 13){ ProjectedTexture = texture(ProjTex11, ProjectorSpaceCoords.st); }
		if(inputID == 14){ ProjectedTexture = texture(ProjTex12, ProjectorSpaceCoords.st); }
		if(inputID == 15){ ProjectedTexture = texture(ProjTex13, ProjectorSpaceCoords.st); }
		if(inputID == 16){ ProjectedTexture = texture(ProjTex14, ProjectorSpaceCoords.st); }
		if(inputID == 17){ ProjectedTexture = texture(ProjTex15, ProjectorSpaceCoords.st); }
		
		// clamp to 0-1 range
		ProjectedTexture = clamp( ProjectedTexture , 0 , 1 );

		// mask it
		ProjectedTexture *= ProjectorMask * FadeScale;
		return ProjectedTexture;
	}
	else{
		return vec4(0);
	}
}



float Contribute_Texture_To_Buffer( vec4 color , vec4 SampledTexture , ProjectorObject pObj , int currentChanIndex , vec4 constColor , float projectorMask ){
	/////////////// for FIXTURES
	ivec4 Routing = ivec4( pObj.Routingr , pObj.Routingg , pObj.Routingb , pObj.Routinga );

	SampledTexture = clamp(SampledTexture + constColor,0,1) * projectorMask;

	SampledTexture = pow(SampledTexture, vec4(1.0/pObj.Gamma)); // GAMMA
	SampledTexture *= pObj.Gain; // GAIN
	

	if (pObj.Projectorblendmode == 0){ // ADD
		color.r += SampledTexture.r * float(currentChanIndex == pObj.Routingr);
		color.r += SampledTexture.g * float(currentChanIndex == pObj.Routingg);
		color.r += SampledTexture.b * float(currentChanIndex == pObj.Routingb);
		color.r += SampledTexture.a * float(currentChanIndex == pObj.Routinga);
	}

	else if (pObj.Projectorblendmode == 1){ // MAX
		color.r = max( color.r , SampledTexture.r * float(currentChanIndex == pObj.Routingr) );
		color.r = max( color.r , SampledTexture.g * float(currentChanIndex == pObj.Routingg) );
		color.r = max( color.r , SampledTexture.b * float(currentChanIndex == pObj.Routingb) );
		color.r = max( color.r , SampledTexture.a * float(currentChanIndex == pObj.Routinga) );
	}
	
	else if (pObj.Projectorblendmode == 2){ // MIN
		color.r = min( color.r , SampledTexture.r * float(currentChanIndex == pObj.Routingr) );
		color.r = min( color.r , SampledTexture.g * float(currentChanIndex == pObj.Routingg) );
		color.r = min( color.r , SampledTexture.b * float(currentChanIndex == pObj.Routingb) );
		color.r = min( color.r , SampledTexture.a * float(currentChanIndex == pObj.Routinga) );
	}

	else if (pObj.Projectorblendmode == 3){ // MULTIPLY
		color.r = mix( color.r , color.r*SampledTexture.r , float(currentChanIndex == pObj.Routingr) );
		color.r = mix( color.r , color.r*SampledTexture.g , float(currentChanIndex == pObj.Routingg) );
		color.r = mix( color.r , color.r*SampledTexture.b , float(currentChanIndex == pObj.Routingb) );
		color.r = mix( color.r , color.r*SampledTexture.a , float(currentChanIndex == pObj.Routinga) );
	}

	else if (pObj.Projectorblendmode == 4){ // OVER
		// out = alpha * new + (1 - alpha) * old
		float alpha_a = SampledTexture.a;
		float alpha_r = alpha_a * float(( currentChanIndex == pObj.Routingr ));
		float alpha_g = alpha_a * float(( currentChanIndex == pObj.Routingg ));
		float alpha_b = alpha_a * float(( currentChanIndex == pObj.Routingb ));

		color.r = alpha_r * SampledTexture.r + (1 - alpha_r) * color.r;
		color.r = alpha_g * SampledTexture.g + (1 - alpha_g) * color.r;
		color.r = alpha_b * SampledTexture.b + (1 - alpha_b) * color.r;
		color.r = alpha_a * SampledTexture.a + (1 - alpha_a) * color.r;
	}
	

	return color.r;

}


vec4 Contribute_Texture_To_Buffer( vec4 color , vec4 SampledTexture , ProjectorObject pObj , ivec3 rgbID , vec4 constColor , vec3 projectorMask ){
	/////////////// for SURFACES
	ivec4 Routing = ivec4( pObj.Routingr , pObj.Routingg , pObj.Routingb , pObj.Routinga );


	SampledTexture = clamp(SampledTexture + constColor,0,1);
	SampledTexture.rgb *= projectorMask;

	SampledTexture = pow(SampledTexture, vec4(1.0/pObj.Gamma)); // GAMMA
	SampledTexture *= pObj.Gain; // GAIN


	
	if (pObj.Projectorblendmode == 0){ // ADD
		if( rgbID.r == pObj.Routingr ){    color.r += SampledTexture.r ; color.a += SampledTexture.a;   	}
		if( rgbID.g == pObj.Routingg ){    color.g += SampledTexture.g ; color.a += SampledTexture.a;   	}
		if( rgbID.b == pObj.Routingb ){    color.b += SampledTexture.b ; color.a += SampledTexture.a;   	}
	}
	
	else if (pObj.Projectorblendmode == 1){ // MAX
		if( rgbID.r == pObj.Routingr ){    color.r = max( color.r , SampledTexture.r ) ; color.a = max( color.a , SampledTexture.a ) ;  	}
		if( rgbID.g == pObj.Routingg ){    color.r = max( color.g , SampledTexture.g ) ; color.a = max( color.a , SampledTexture.a ) ;   	}
		if( rgbID.b == pObj.Routingb ){    color.r = max( color.b , SampledTexture.b ) ; color.a = max( color.a , SampledTexture.a ) ;   	}
		// if( currentChanIndex == pObj.Routinga ){    color.r = max( color.r , SampledTexture.a ) ;   	}
	}
	
	else if (pObj.Projectorblendmode == 2){ // MIN
		if( rgbID.r == pObj.Routingr ){    color.r = min( color.r , SampledTexture.r ) ; color.a = min( color.a , SampledTexture.a ) ;   	}
		if( rgbID.g == pObj.Routingg ){    color.r = min( color.g , SampledTexture.g ) ; color.a = min( color.a , SampledTexture.a ) ;   	}
		if( rgbID.b == pObj.Routingb ){    color.r = min( color.b , SampledTexture.b ) ; color.a = min( color.a , SampledTexture.a ) ;   	}
		// if( currentChanIndex == pObj.Routinga ){    color.r = min( color.r , SampledTexture.a ) ;   	}
	}

	else if (pObj.Projectorblendmode == 3){ // MULTIPLY
		if( rgbID.r == pObj.Routingr ){    color.r *= SampledTexture.r ; color.r *= SampledTexture.a ;   	}
		if( rgbID.g == pObj.Routingg ){    color.g *= SampledTexture.g ; color.g *= SampledTexture.a ;   	}
		if( rgbID.b == pObj.Routingb ){    color.b *= SampledTexture.b ; color.b *= SampledTexture.a ;   	}
		// if( rgbID.a == pObj.Routinga ){    color.a *= SampledTexture.a ; color.a *= SampledTexture.a ;   	} // can't do alpha, surfaces only can display r/g/b
	}

	else if (pObj.Projectorblendmode == 4){ // OVER
		// out = alpha * new + (1 - alpha) * old
		float alpha = SampledTexture.a;
		if( rgbID.r == pObj.Routingr ){    color.r = alpha * SampledTexture.r + (1 - alpha) * color.r ; color.a = alpha * SampledTexture.a + (1 - alpha) * color.a ;   	}
		if( rgbID.g == pObj.Routingg ){    color.g = alpha * SampledTexture.g + (1 - alpha) * color.g ; color.a = alpha * SampledTexture.a + (1 - alpha) * color.a ;   	}
		if( rgbID.b == pObj.Routingb ){    color.b = alpha * SampledTexture.b + (1 - alpha) * color.b ; color.a = alpha * SampledTexture.a + (1 - alpha) * color.a ;   	}
		// if( currentChanIndex == pObj.Routinga ){    color.r = alpha * SampledTexture.a + (1 - alpha) * color.r ;   	}
	}
	// 


	return color;

}


vec4 Apply_Extend_Modes( vec4 ProjectorSpaceCoords , ProjectorObject pObj ){

	if( pObj.Pextend == 0 ){ // ZERO
		// do nothing, this is the default mode.
	}
	else if( pObj.Pextend == 1 ){ // EXTEND
		ProjectorSpaceCoords.xy = clamp(ProjectorSpaceCoords.xy,vec2(0.0001),vec2(0.99999));
	}
	else if( pObj.Pextend == 2 ){ // CYCLE
		ProjectorSpaceCoords.xy = mod(ProjectorSpaceCoords.xy,1);
	}
	else if( pObj.Pextend == 3 ){ // MIRROR
		ProjectorSpaceCoords.xy = fract(ProjectorSpaceCoords.xy*0.5)*2.0;
		ProjectorSpaceCoords.xy = 1 - abs(ProjectorSpaceCoords.xy-1);
	}

	return ProjectorSpaceCoords;
	
}


float Contribute_SelectionHighlight_To_Buffer( vec4 color , bool SelectedState , int currentChanIndex ){
	/////////////////////// for fixtures
	if(SelectedState){
		if( currentChanIndex == ViewportChanIndicies.x ){ // red
			// color.r *= 0.25;
			color.r = mix( color.r , color.r*.25 , selectionPulse );
		}
		if( currentChanIndex == ViewportChanIndicies.y ){ // green
			// color.r *= 0.25;
			// color.r = max(color.r,selectionPulse*.75);
			color.r = mix( color.r , 0.75 , selectionPulse );
		}
		if( currentChanIndex == ViewportChanIndicies.z ){ // blue
			color.r = mix( color.r , color.r*.25 , selectionPulse );
		}
	}

	return color.r;
	
}



vec4 Contribute_SelectionHighlight_To_Buffer( vec4 color , bool SelectedState ){
	 /////////////////// for surfaces
	if(SelectedState){
		color.r = mix( color.r , color.r*.25 , selectionPulse );
		color.g = mix( color.g , 0.75 , selectionPulse );
		color.b = mix( color.b , color.b*.25 , selectionPulse );
	}

	return color;
	
}


float Apply_PixFrames( vec4 color , ivec2 PixelCoords2D , int numPixframes , int NumberOfControls ){
	/////////////////// FOR FIXTURES

	float PixFrameAccum = 0.0;
	// numPixframes= 2;

	for( int ContributionIndex=0; ContributionIndex<numPixframes; ContributionIndex++ )
	{
		
		int Index = int(texelFetch( PixframeControl , (ContributionIndex*NumberOfControls)+0 ).r); // Index
		float Intensity = texelFetch( PixframeControl , (ContributionIndex*NumberOfControls)+1 ).r; // Intensity
		int Blendmode = int(texelFetch( PixframeControl , (ContributionIndex*NumberOfControls)+2 ).r); // Add, Max, Min, Multiply, Over

		float PixFrameVal = texelFetch(PIXFRAMES, ivec3(PixelCoords2D,Index) , 0).r;
		bool isNOTpassthrough = PixFrameVal >= 0.0; // this will be == 1 if the value is not -1. -1 means passthrough.
		
		if( isNOTpassthrough == true ){
			PixFrameVal = map( PixFrameVal , 0.0 , 255.0 , 0.0 , 1.0 );

			if( Blendmode == 0 ){ // ADD
				PixFrameAccum = mix( PixFrameAccum , PixFrameAccum + PixFrameVal , Intensity );
			}

			if( Blendmode == 1 ){ // MAX
				PixFrameAccum = mix( PixFrameAccum , max(PixFrameAccum , PixFrameVal) , Intensity );
			}

			if( Blendmode == 2 ){ // MIN
				PixFrameAccum = mix( PixFrameAccum , min(PixFrameAccum , PixFrameVal) , Intensity );
			}

			if( Blendmode == 3 ){ // MULTIPLY
				PixFrameAccum = mix( PixFrameAccum , PixFrameAccum * PixFrameVal , Intensity );
			}

			if( Blendmode == 4 ){ // OVER (Intensity acts as alpha)
				PixFrameAccum = mix( PixFrameAccum , PixFrameVal , Intensity );
			}
		}
	}

	// ensure the value is clamped to the normalized 0-1 range.
	PixFrameAccum = clamp( PixFrameAccum , 0.0 , 1.0 );

	return color.r + PixFrameAccum;
}


vec3 Apply_PixFrames( vec4 color , int surfaceIndex , int numPixframes , int NumberOfControls ){
	/////////////////// FOR SURFACES

	vec3 PixFrameAccum = vec3(0.0);

	for( int ContributionIndex=0; ContributionIndex<numPixframes; ContributionIndex++ )
	{
		
		int Index = int(texelFetch( PixframeControl , (ContributionIndex*NumberOfControls)+0 ).r); // Index
		float Intensity = texelFetch( PixframeControl , (ContributionIndex*NumberOfControls)+1 ).r; // Intensity
		int Blendmode = int(texelFetch( PixframeControl , (ContributionIndex*NumberOfControls)+2 ).r); // Add, Max, Min, Multiply, Over

		vec3 PixFrameVal = texelFetch(SurfacePixframeSampler, ivec2(surfaceIndex,Index) , 0).rgb;
		bvec3 isNOTpassthrough = bvec3( PixFrameVal.r>=0.0 , PixFrameVal.g>=0.0 , PixFrameVal.b>=0.0 ); // this will be == 1 if the value is not -1. -1 means passthrough.
		// vec3 isNOTpassthrough_mask = vec3( isNOTpassthrough );
		
		PixFrameVal = map( PixFrameVal , 0.0 , 255.0 , 0.0 , 1.0 );

		if( Blendmode == 0 ){ // ADD
			if (isNOTpassthrough.r == true){ PixFrameAccum.r = mix( PixFrameAccum.r , PixFrameAccum.r + PixFrameVal.r , Intensity ); }
			if (isNOTpassthrough.g == true){ PixFrameAccum.g = mix( PixFrameAccum.g , PixFrameAccum.g + PixFrameVal.g , Intensity ); }
			if (isNOTpassthrough.b == true){ PixFrameAccum.b = mix( PixFrameAccum.b , PixFrameAccum.b + PixFrameVal.b , Intensity ); }
			// color.r += 1;
		}

		if( Blendmode == 1 ){ // MAX
			if (isNOTpassthrough.r == true){ PixFrameAccum.r = mix( PixFrameAccum.r , max(PixFrameAccum.r , PixFrameVal.r) , Intensity ); }
			if (isNOTpassthrough.g == true){ PixFrameAccum.g = mix( PixFrameAccum.g , max(PixFrameAccum.g , PixFrameVal.g) , Intensity ); }
			if (isNOTpassthrough.b == true){ PixFrameAccum.b = mix( PixFrameAccum.b , max(PixFrameAccum.b , PixFrameVal.b) , Intensity ); }
		}

		if( Blendmode == 2 ){ // MIN
			if (isNOTpassthrough.r == true){ PixFrameAccum.r = mix( PixFrameAccum.r , min(PixFrameAccum.r , PixFrameVal.r) , Intensity ); }
			if (isNOTpassthrough.g == true){ PixFrameAccum.g = mix( PixFrameAccum.g , min(PixFrameAccum.g , PixFrameVal.g) , Intensity ); }
			if (isNOTpassthrough.b == true){ PixFrameAccum.b = mix( PixFrameAccum.b , min(PixFrameAccum.b , PixFrameVal.b) , Intensity ); }
		}

		if( Blendmode == 3 ){ // MULTIPLY
			if (isNOTpassthrough.r == true){ PixFrameAccum.r = mix( PixFrameAccum.r , PixFrameAccum.r * PixFrameVal.r , Intensity ); }
			if (isNOTpassthrough.g == true){ PixFrameAccum.g = mix( PixFrameAccum.g , PixFrameAccum.g * PixFrameVal.g , Intensity ); }
			if (isNOTpassthrough.b == true){ PixFrameAccum.b = mix( PixFrameAccum.b , PixFrameAccum.b * PixFrameVal.b , Intensity ); }
		}

		if( Blendmode == 4 ){ // OVER (Intensity acts as alpha)
			if (isNOTpassthrough.r == true){ PixFrameAccum.r = mix( PixFrameAccum.r , PixFrameVal.r , Intensity ); }
			if (isNOTpassthrough.g == true){ PixFrameAccum.g = mix( PixFrameAccum.g , PixFrameVal.g , Intensity ); }
			if (isNOTpassthrough.b == true){ PixFrameAccum.b = mix( PixFrameAccum.b , PixFrameVal.b , Intensity ); }
		}
	}

	// ensure the value is clamped to the normalized 0-1 range.
	PixFrameAccum = clamp( PixFrameAccum , 0.0 , 1.0 );

	return color.rgb + PixFrameAccum;
}

float Generate_Projector_Masks_V2( ProjectorObject pObj , int currentChanIndex , int surfIndex ){
	/////////////////// FOR SURFACES
	float MaskCumulative = -1.0;
	float MaskVal = 0.0;
	int MaskIndex = 0;

	if( pObj.NumMasksR > 0 ){
		for( int i=0; i<pObj.NumMasksR; i++ ){
			MaskIndex = pObj.Masks_r[i];
			if( MaskIndex >= 0  && currentChanIndex == pObj.Routingr ){
				MaskVal = texelFetch(SurfaceMaskSampler, ivec2( surfIndex , MaskIndex ) , 0 ).r;
				MaskCumulative = max( MaskCumulative , MaskVal );
			}
		} 
	}

	if( pObj.NumMasksG > 0 ){
		for( int i=0; i<pObj.NumMasksG; i++ ){
			MaskIndex = pObj.Masks_g[i];
			if( MaskIndex >= 0  && currentChanIndex == pObj.Routingg ){
				MaskVal = texelFetch(SurfaceMaskSampler, ivec2( surfIndex , MaskIndex ) , 0 ).r;
				MaskCumulative = max( MaskCumulative , MaskVal );
			}
		}
	}

	if( pObj.NumMasksB > 0 ){
		for( int i=0; i<pObj.NumMasksB; i++ ){
			MaskIndex = pObj.Masks_b[i];
			if( MaskIndex >= 0  && currentChanIndex == pObj.Routingb ){
				MaskVal = texelFetch(SurfaceMaskSampler, ivec2( surfIndex , MaskIndex ) , 0 ).r;
				MaskCumulative = max( MaskCumulative , MaskVal );
			}
		}
	}

	if( pObj.NumMasksA > 0 ){
		for( int i=0; i<pObj.NumMasksA; i++ ){
			MaskIndex = pObj.Masks_a[i];
			if( MaskIndex >= 0  && currentChanIndex == pObj.Routinga ){
				MaskVal = texelFetch(SurfaceMaskSampler, ivec2( surfIndex , MaskIndex ) , 0 ).r;
				MaskCumulative = max( MaskCumulative , MaskVal );
			}
		}
	}

	if( MaskCumulative < 0 ){ MaskCumulative = 1; }

	return MaskCumulative;
}


float Generate_Projector_Masks_V2( ivec2 PixelCoords2D , ProjectorObject pObj , int currentChanIndex ){
	/////////////////// FOR FIXTURES
	float MaskCumulative = -1.0;
	float MaskVal = 0.0;
	int MaskIndex = 0;

	if( pObj.NumMasksR > 0 ){
		for( int i=0; i<pObj.NumMasksR; i++ ){
			MaskIndex = pObj.Masks_r[i];
			if( MaskIndex >= 0  && currentChanIndex == pObj.Routingr ){
				MaskVal = texelFetch(MASKS, ivec3( PixelCoords2D , MaskIndex ) , 0 ).r;
				MaskCumulative = max( MaskCumulative , MaskVal );
			}
		} 
	}

	if( pObj.NumMasksG > 0 ){
		for( int i=0; i<pObj.NumMasksG; i++ ){
			MaskIndex = pObj.Masks_g[i];
			if( MaskIndex >= 0  && currentChanIndex == pObj.Routingg ){
				MaskVal = texelFetch(MASKS, ivec3( PixelCoords2D , MaskIndex ) , 0 ).r;
				MaskCumulative = max( MaskCumulative , MaskVal );
			}
		}
	}

	if( pObj.NumMasksB > 0 ){
		for( int i=0; i<pObj.NumMasksB; i++ ){
			MaskIndex = pObj.Masks_b[i];
			if( MaskIndex >= 0  && currentChanIndex == pObj.Routingb ){
				MaskVal = texelFetch(MASKS, ivec3( PixelCoords2D , MaskIndex ) , 0 ).r;
				MaskCumulative = max( MaskCumulative , MaskVal );
			}
		}
	}

	if( pObj.NumMasksA > 0 ){
		for( int i=0; i<pObj.NumMasksA; i++ ){
			MaskIndex = pObj.Masks_a[i];
			if( MaskIndex >= 0  && currentChanIndex == pObj.Routinga ){
				MaskVal = texelFetch(MASKS, ivec3( PixelCoords2D , MaskIndex ) , 0 ).r;
				MaskCumulative = max( MaskCumulative , MaskVal );
			}
		}
	}

	if( MaskCumulative < 0 ){ MaskCumulative = 1; }

	return MaskCumulative;
}


vec4 Apply_Projector_Masks( vec4 color , ivec2 PixelCoords2D , int surfIndex , ProjectorObject pObj ){
	/////////////////// FOR SURFACES
	//////////////// NEEDS TO BE UPDATED TO WORK WITH MULTIPLE MASKS! 
	//////////////// SEE FIXTURE MASK GEN V2 FUNCTION.

	texelFetch( SurfaceMaskSampler , ivec2(surfIndex,0) , 0 );

	// these if statements are wrong. pObj.NumMasksR is the number of masks, and should control the length of for loop.
	if(pObj.NumMasksR >= 0 && ViewportChanIndicies.r == pObj.Routingr){
		color.r *= texelFetch( SurfaceMaskSampler , ivec2(surfIndex,pObj.Routingr) , 0 ).r;
	}

	if(pObj.NumMasksG >= 0 && ViewportChanIndicies.g == pObj.Routingg){
		color.g *= texelFetch( SurfaceMaskSampler , ivec2(surfIndex,pObj.Routingg) , 0 ).r;
	}

	if(pObj.NumMasksB >= 0 && ViewportChanIndicies.b == pObj.Routingb){
		color.b *= texelFetch( SurfaceMaskSampler , ivec2(surfIndex,pObj.Routingb) , 0 ).r;
	}

	return color;
}


float Contribute_MaskHighlight_To_Buffer( vec4 color , ivec2 PixelCoords2D , int currentChanIndex ){
	///////////// FOR FIXTURE
	if(maskPreviewIndex >= 0){

		float hoveredMask = texelFetch(MASKS, ivec3(PixelCoords2D,maskPreviewIndex) , 0).r;

		if( currentChanIndex == ViewportChanIndicies.x ){ // red
			// color.r = mix( color.r , color.r*.1 , hoveredMask );
			color.r = mix( color.r*.00 , 0.5 , hoveredMask );
		}
		if( currentChanIndex == ViewportChanIndicies.y ){ // green
			color.r = mix( color.r*.00 , color.r*.08 , hoveredMask );
			// color.r = mix( color.r , 0.5 , hoveredMask );
		}
		if( currentChanIndex == ViewportChanIndicies.z ){ // blue
			// color.r = mix( color.r , color.r*.1 , hoveredMask );
			color.r = mix( color.r*.00 , 0.75 , hoveredMask );
		}
	}
	
	return color.r;
}


vec4 Contribute_MaskHighlight_To_Buffer( vec4 color , int surfIndex , ivec3 RGB_IDs ){
	///////////// FOR SURFACES
	if(maskPreviewIndex >= 0){

		float hoveredMask = texelFetch(SurfaceMaskSampler, ivec2(surfIndex,maskPreviewIndex) , 0).r;

		color.r = mix( color.r*.00 , 0.5 , hoveredMask );
		color.g = mix( color.g*.00 , color.g*.08 , hoveredMask );
		color.b = mix( color.b*.00 , 0.75 , hoveredMask );
	}
	
	return color;
}


vec4 Contribute_ConstantColor_To_Buffer( ProjectorObject pObj , int currentChanIndex , float ProjectorMask ){
	////////////// FIXTURES
	
	ivec4 Routing = ivec4( pObj.Routingr , pObj.Routingg , pObj.Routingb , pObj.Routinga );

	vec4 returnVal = vec4(0.0);

	returnVal.r += pObj.Setcolorr * ProjectorMask * float(currentChanIndex == Routing.r) ;
	returnVal.g += pObj.Setcolorg * ProjectorMask * float(currentChanIndex == Routing.g) ;
	returnVal.b += pObj.Setcolorb * ProjectorMask * float(currentChanIndex == Routing.b) ;
	returnVal.a += pObj.Setcolora * ProjectorMask * float(currentChanIndex == Routing.a) ;

	return returnVal;

}


vec4 Contribute_ConstantColor_To_Buffer( ProjectorObject pObj , ivec3 rgbID , float ProjectorMask ){
	////////////// SURFACES

	return vec4( pObj.Setcolorr , pObj.Setcolorg , pObj.Setcolorb , pObj.Setcolora ) * ProjectorMask;

}